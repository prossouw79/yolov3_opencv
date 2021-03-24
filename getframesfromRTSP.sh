#!/bin/bash

rm -rf input/*

gst-launch-1.0 rtspsrc location=$RTSP_URL latency=200 ! queue ! rtph264depay ! avdec_h264 ! videorate ! video/x-raw,framerate=1000/1001 ! jpegenc ! multifilesink location="./input/$CAM_NAME-frame%020d.jpg"