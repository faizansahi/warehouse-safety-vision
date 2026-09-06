"""Minimal OpenCV source loop for webcam, video files, or RTSP URLs."""

import os

import cv2

from warehouse_vision.detector import YoloDetector

source = os.getenv("VIDEO_SOURCE", "0")
source = int(source) if source.isdigit() else source
capture = cv2.VideoCapture(source)
detector = YoloDetector(os.getenv("YOLO_WEIGHTS", "yolo11n.pt"))
while capture.isOpened():
    ok, frame = capture.read()
    if not ok:
        break
    detector.detect(frame)
capture.release()
