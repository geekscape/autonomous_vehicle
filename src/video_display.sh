#!/bin/sh

# DEBUG=-v
# DEBUG=--gst-debug-level=3

PORT=5000

if [ "$1" != "" ]; then
  PORT=$1
fi

# MJPEG / RTP / UDP
gst-launch-1.0 $DEBUG udpsrc port=$PORT caps='application/x-rtp, encoding-name=JPEG, payload=26' ! rtpjpegdepay ! jpegdec ! videoconvert ! osxvideosink

# H.265 / RTP / UDP
# gst-launch-1.0 $DEBUG udpsrc port=$PORT caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! avdec_h264 ! videoconvert ! osxvideosink
