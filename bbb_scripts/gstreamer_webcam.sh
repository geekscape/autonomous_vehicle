#!/bin/sh
#
# Installation
# ~~~~~~~~~~~~
# apt-get install gstreamer-1.0 gstreamer1.0-tools
# apt-get install gstreamer1.0-plugins-base gstreamer1.0-plugins-good
# apt-get install gstreamer1.0-plugins-bad  gstreamer1.0-plugins-ugly

REMOTE_HOST=CHANGE_ME.local
REMOTE_PORT=5000

DEVICE=/dev/video0
WIDTH=320
HEIGHT=176
FRAME_RATE=15/1

v4l2-ctl --set-fmt-video=width=$WIDTH,height=$HEIGHT,pixelformat=YUYV
v4l2-ctl -p 15

gst-launch-1.0 v4l2src device=$DEVICE !  \
  video/x-raw,width=$WIDTH,height=$HEIGHT,framerate=$FRAME_RATE !  \
  jpegenc ! rtpjpegpay !  \
  udpsink host=$REMOTE_HOST port=$REMOTE_PORT &
