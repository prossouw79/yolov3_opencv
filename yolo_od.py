""" Implimentation of YOLO v3 object detection  by Chieko N."""

import numpy as np
import argparse
import time
import cv2
import os
import glob
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from yolo_od_utils import yolo_object_detection

# Get options specified in the command line
parser = argparse.ArgumentParser()
parser.add_argument('-id', '--input', type=str, default='input')
parser.add_argument('-od', '--output', type=str, default='output')
parser.add_argument('-c', '--confidence', type=float, default=0.5)
parser.add_argument('-t', '--threshold', type=float, default=0.5)
args = parser.parse_args()

print("Cleaning up {}", args.input)
files = glob.glob('./' + args.input + '/*')
for f in files:
    os.remove(f)

print("Cleaning up {}", args.output)
files = glob.glob('./' + args.output + '/*')
for f in files:
    os.remove(f)

print('Starting GStreamer script to pull images from RTSP')
# Run script that uses gstreamer to capture frames
p = subprocess.Popen("./getframesfromRTSP.sh")

# set filenames for the model
coco_names_file = "yolo/coco.names"
yolov3_weight_file = "yolo/yolov3.weights"
yolov3_config_file = "yolo/yolov3.cfg"

# read coco object names
LABELS = open(coco_names_file).read().strip().split("\n")

# assign rondom colours to the corresponding class labels
np.random.seed(45)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")

# read YOLO network model
net = cv2.dnn.readNetFromDarknet(yolov3_config_file, yolov3_weight_file)

patterns=['*']
ignore_patterns = ['*.txt','*.YOLO.jpg']
ignore_directories = False
case_sensitive = False
patternMatchingEventHandler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

def on_created(event):
    time.sleep(0.1)
    img = event.src_path.split('.jpg', 1)[0] + '.jpg'
    if(os.path.isfile(img)):
        yolo_object_detection(img, net, args.confidence, args.threshold, LABELS, COLORS, args.output)

patternMatchingEventHandler.on_created = on_created

go_recursively = True
folderObserver = Observer()
folderObserver.schedule(patternMatchingEventHandler, args.input, recursive=go_recursively)

folderObserver.start()
        
try:
    while True:
        time.sleep(0.25)
except KeyboardInterrupt:
    folderObserver.stop()
    folderObserver.join()