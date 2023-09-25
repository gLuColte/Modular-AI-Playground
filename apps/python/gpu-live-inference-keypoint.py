##########################################################
####################### Libraries ########################
##########################################################
import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
import os
import subprocess
from torchvision import transforms
import numpy as np
import time

##########################################################
###################### Parameters ########################
##########################################################
# environment:
#     - RUN_TYPE=python
#     - RUN_SCRIPT_PATH=apps/python/gpu-live-inference-keypoint.py
#     - MODEL_PATH=yolo-Weights/yolov8n-pose.pt
#     - VISUALIZATION=0
#     - RTSP_INPUT=rtsp://emulator-module:8554/sample-1 
#     - RTSP_OUTPUT=rtsp://emulator-module:8554/live-1
##########################################################
####################### Functions ########################
##########################################################

def open_ffmpeg_stream_process(stream_path):
    args = (
        "ffmpeg -re -f rawvideo -pix_fmt "
        "rgb24 -s 1920x1080 -i pipe:0 -pix_fmt yuvj420p "
        f"-f rtsp {stream_path}"
    ).split()
    return subprocess.Popen(args, stdin=subprocess.PIPE)


##########################################################
######################### Main ###########################
##########################################################
if __name__ == "__main__":
    # Initialize Model
    model_path=os.environ['MODEL_PATH']
    model = YOLO(model_path)
    
    # RUN
    input_stream=os.environ['RTSP_INPUT']
    output_stream=os.environ['RTSP_OUTPUT']
    visualization=bool(int(os.environ['VISUALIZATION']))
    ffmpeg_process = open_ffmpeg_stream_process(output_stream)
    capture = cv2.VideoCapture(input_stream)    
    while True:
        success, img = capture.read()
        if not success:
            print("Failed to grab")
            time.sleep(1)
            continue
        results = model(img, stream=True)
        if visualization:
            # coordinates
            for r in results:
                img = r.plot()
        ffmpeg_process.stdin.write(img.astype(np.uint8).tobytes())
        
    capture.release()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()