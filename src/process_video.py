#!/usr/bin/env python
#
# Notes
# ~~~~~
# Recorded telemetry columns for each released version ...
#  0: "version number", "throttle", "steering"
#  1: "version number", "frame_id", "throttle", "steering"
#
# Requirements
# ~~~~~~~~~~~~
# pip install dronekit
#
# To Do
# ~~~~~
# - None, yet.
#
# Resources
# ~~~~~~~~~
# http://stackoverflow.com/questions/36768245/udp-videostreaming-in-gstreamer-with-python
# https://cgit.freedesktop.org/gstreamer/gst-plugins-good/tree/gst/rtp/README
#
# /Users/andyg/archive/Documents/play/python/gstreamer/example_4.py
#
# Test: python -c "import cv2; print(cv2.getBuildInformation())"

import cv2
import numpy
import sys

# -----------------------------------------------------------------------------

from dronekit import connect, VehicleMode
from pymavlink import mavutil

HOST_IP_PORT = 'udp:127.0.0.1:14550'

vehicle = connect(HOST_IP_PORT, wait_ready=True)

# -----------------------------------------------------------------------------

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

VIDEO_INPUT_PORT  = 5000
VIDEO_OUTPUT_PORT = 5001

# -----------------------------------------------------------------------------
# Create video output pipeline

video_output_pipeline = (
  'appsrc name="appsrc" ! videoconvert ! %s ! udpsink host=%s port=%s')

video_output = Gst.parse_launch(video_output_pipeline %
# ("jpegenc    ! rtpjpegpay", "127.0.0.1", str(VIDEO_OUTPUT_PORT)))  # MJPEG
("vtenc_h264 ! rtph264pay config-interval=5 pt=96", "127.0.0.1", str(VIDEO_OUTPUT_PORT)))  # Mac OS X H.264
# ("omxh264enc ! rtph264pay config-interval=5 pt=96", REMOTE_HOST, str(VIDEO_OUTPUT_PORT)))  # Raspberry Pi H.264

caps = Gst.caps_from_string(
  'video/x-raw, format=RGB, width=320, height=176, framerate=15/1')

appsrc = video_output.get_child_by_name('appsrc')
appsrc.props.caps = caps
appsrc.props.stream_type  = 0  # GST_APP_STREAM_TYPE_STREAM
appsrc.props.is_live      = True
appsrc.props.do_timestamp = True
appsrc.props.format       = Gst.Format.TIME

video_output.set_state(Gst.State.PLAYING)

# -----------------------------------------------------------------------------
# Create video input pipeline

frame_id  = 0
image_bgr = None

def gst_to_opencv(sample):
  buffer = sample.get_buffer()
  caps   = sample.get_caps()
  format = caps.get_structure(0).get_value('format')
  width  = caps.get_structure(0).get_value('width')
  height = caps.get_structure(0).get_value('height')
  buffer_size = buffer.get_size()

  opencv_array = numpy.ndarray((height, width, 3),
    buffer=buffer.extract_dup(0, buffer_size), dtype=numpy.uint8)
  return opencv_array

def new_buffer(sink, data):
  global frame_id, image_bgr
  sample = sink.emit("pull-sample")
  buffer = sample.get_buffer()
# timestamp = buffer.pts
  frame_id += 1
  image_bgr = gst_to_opencv(sample)
  return Gst.FlowReturn.OK

source   = Gst.ElementFactory.make("udpsrc", None)
depay    = Gst.ElementFactory.make("rtpjpegdepay", None)
decoder  = Gst.ElementFactory.make("jpegdec", None)
convert  = Gst.ElementFactory.make("videoconvert", None)
sink     = Gst.ElementFactory.make("appsink", None)
pipeline = Gst.Pipeline.new("test-pipeline")

if not pipeline:
  print("ERROR: GStreamer failed to create video pipeline")
  exit(-1)

source.set_property("port", VIDEO_INPUT_PORT)
source.set_property("caps", Gst.caps_from_string(
  "application/x-rtp, encoding-name=JPEG, payload=26"))

sink.set_property("caps", Gst.caps_from_string(
  "video/x-raw, format=BGR, width=320, height=176"))

sink.set_property("emit-signals", True)
# sink.set_property("max-buffers", 2)
# sink.set_property("drop", True)
# sink.set_property("sync", False)

sink.connect("new-sample", new_buffer, sink)

pipeline.add(source)
pipeline.add(depay)
pipeline.add(decoder)
pipeline.add(convert)
pipeline.add(sink)

def pipeline_link_error(element1, element2):
  print("ERROR: GStreamer pipeline elements linking: %s to %s" %
    (element1, element2))
  exit(-1)

if not Gst.Element.link(source,  depay):   link_error("source",  "depay")
if not Gst.Element.link(depay,   decoder): link_error("depay",   "decoder")
if not Gst.Element.link(decoder, convert): link_error("decoder", "convert")
if not Gst.Element.link(convert, sink):    link_error("convert", "sink")

error_code = pipeline.set_state(Gst.State.PLAYING)
if error_code == Gst.StateChangeReturn.FAILURE:
  print("Unable to set the pipeline to the playing state")
  exit(-1)

# -----------------------------------------------------------------------------

FONT = cv2.FONT_HERSHEY_SIMPLEX
VERSION = 1

bus = pipeline.get_bus()

video_file = cv2.VideoWriter(
  'z_video.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 10, (320, 176))

def overlay_value(image, value, offset):
  cv2.putText(image_bgr,
    str(value), (offset + 2, 16), FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
  for x in range(0, 10):
    color = (255, 255, 255) if value & 0x200 else (0, 0, 0)
    image = cv2.rectangle(
      image_bgr, (4 * x + offset, 0), (4 * x + offset + 2, 4), color, 2)
    value = value << 1
  return image_bgr

while True:
  message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)

  if image_bgr is not None:   
    throttle = int((vehicle.channels['1'] - 982) / 1.002)
    if throttle < 0: throttle = 0
    steering = 1024 - int((vehicle.channels['3'] - 982) / 1.002)
    if steering > 1024: steering = 512
    image_bgr = overlay_value(image_bgr, VERSION,    0)
    image_bgr = overlay_value(image_bgr, frame_id,  60)
    image_bgr = overlay_value(image_bgr, throttle, 120)
    image_bgr = overlay_value(image_bgr, steering, 180)

    video_file.write(image_bgr)

#   image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_bgr = cv2.resize(image_bgr, (0,0), fx=3.0, fy=3.0)
    cv2.imshow("Gstreamer Video", image_bgr)
    if cv2.waitKey(1) & 0xff == ord('q'): break
    image_bgr = None

#   data = image_rgb.tobytes()
#   buffer = Gst.Buffer.new_allocate(None, len(data), None)
#   buffer.fill(0, data)
#   appsrc.emit('push-buffer', buffer)

  if message:
    if message.type == Gst.MessageType.ERROR:
      err, debug = message.parse_error()
      print("Error received from element %s: %s" % (
        message.src.get_name(), err))
      print("Debugging information: %s" % debug)
      break
    elif message.type == Gst.MessageType.EOS:
      print("GStreaner End-Of-Stream")
      break
    elif message.type == Gst.MessageType.STATE_CHANGED:
      if isinstance(message.src, Gst.Pipeline):
        old_state, new_state, pending_state = message.parse_state_changed()
        print("GStreamer Pipeline state changed from %s to %s" %
          (old_state.value_nick, new_state.value_nick))
    elif message.type == Gst.MessageType.STREAM_STATUS:
      print("GStreamer message received: STREAM_STATUS")
    elif message.type == Gst.MessageType.NEW_CLOCK:
      print("GStreamer message received: NEW_CLOCK")
    elif message.type == Gst.MessageType.STREAM_START:
      print("GStreamer message received: STREAM_START")
    elif message.type == Gst.MessageType.ASYNC_DONE:
      print("GStreamer message received: ASYNC_DONE")
    else:
      print("GStreamer message received: %s" % (message.type))

pipeline.set_state(Gst.State.NULL)
video_file.release()
cv2.destroyAllWindows() 

# -----------------------------------------------------------------------------
