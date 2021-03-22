#!/bin/bash

gst-launch-1.0 rtspsrc location=$RTSP_URL latency=500 ! queue ! rtph264depay ! avdec_h264 ! videorate ! video/x-raw,framerate=1000/1001 ! jpegenc ! multifilesink location="./input/frame%08d.jpg"
