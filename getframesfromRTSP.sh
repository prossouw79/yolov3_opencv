#!/bin/bash

gst-launch-1.0 -q rtspsrc location=$RTSP_URL latency=200 ! queue ! rtph264depay ! avdec_h264 ! videorate ! video/x-raw,framerate=1000/1001 ! jpegenc ! multifilesink location="./input/frame%01d.jpg"
