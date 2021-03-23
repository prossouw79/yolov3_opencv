""" Implimentation of YOLO v3 object detection  by Chieko N."""

import numpy as np
import argparse
import cv2
import os
import time
import sys
import glob
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from yolo_od_utils import yolo_object_detection
from yolo_od_utils import ssim
from yolo_od_utils import mse

# Get options specified in the command line
parser = argparse.ArgumentParser()
parser.add_argument('-id', '--input', type=str, default='input')
parser.add_argument('-od', '--output', type=str, default='output')
parser.add_argument('-mse', '--mseThreshold', type=float, default=0.1)
parser.add_argument('-bf', '--bufferFrames', type=int, default=2)
parser.add_argument('-c', '--confidence', type=float, default=0.65)
parser.add_argument('-t', '--threshold', type=float, default=0.5)
args = parser.parse_args()

# set filenames for the model
coco_names_file = "yolo/coco.names"
yolov3_weight_file = "yolo/yolov3.weights"
yolov3_config_file = "yolo/yolov3.cfg"

frameBuffer = []
countdown = 0

# read coco object names
LABELS = open(coco_names_file).read().strip().split("\n")

# assign rondom colours to the corresponding class labels
np.random.seed(45)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")

# read YOLO network model
net = cv2.dnn.readNetFromDarknet(yolov3_config_file, yolov3_weight_file)

patterns = ['*']
ignore_patterns = ['*.txt', '*.YOLO.jpg']
ignore_directories = False
case_sensitive = False
patternMatchingEventHandler = PatternMatchingEventHandler(
    patterns, ignore_patterns, ignore_directories, case_sensitive)


def on_created(event):
    time.sleep(0.1)
    img = event.src_path.split('.jpg', 1)[0] + '.jpg'
    if(os.path.isfile(img)):
        global frameBuffer
        global countdown
                
        if(len(frameBuffer) > args.bufferFrames):
            frameBuffer.pop(0)

        if(countdown > 0):
            print("Countdown ", countdown)
            objects_detected = yolo_object_detection(img, net, args.confidence, args.threshold, LABELS, COLORS, args.output)
            if(objects_detected):
                countdown = 10
            else:
                countdown = countdown - 1
        else:
            diffs = []
            for historicFrame in frameBuffer:
                m = mse(historicFrame, img, 576)
                diffs.append(m)
                avgMSE = round(sum(diffs) / len(diffs))
                frameDiffMSE = round(abs(m - avgMSE) / avgMSE, 2)
                if(frameDiffMSE > args.mseThreshold):
                    # print("Frame change detected: ", frameDiffMSE)
                    objects_detected = yolo_object_detection(img, net, args.confidence, args.threshold, LABELS, COLORS, args.output)
                    if(objects_detected):
                        countdown = 10

        frameBuffer.append(img)
        #Clean up input directory of older files
        files_in_input_dir = os.listdir(args.input)
        now = time.time()
        for f in files_in_input_dir:
            if f.lower().endswith(".jpg"):
                path = args.input + "/" + f
                file_age = os.stat(path).st_mtime
                if file_age < (now - 10):
                    if os.path.isfile(path):
                        os.unlink(path)


patternMatchingEventHandler.on_created = on_created

go_recursively = True
folderObserver = Observer()
folderObserver.schedule(patternMatchingEventHandler,
                        args.input, recursive=go_recursively)

folderObserver.start()

try:
    while True:
        time.sleep(0.25)
except KeyboardInterrupt:
    folderObserver.stop()
    folderObserver.join()
