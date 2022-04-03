import cv2
import numpy as np
import time 


class Camera:
    def __init__(self):
        self.camera  = self.create_camera_instance()
        if(self.camera  == None):
            print("Camera not found")
            return
        time.sleep(2)
        print("Camera ready .....")
        
    def create_camera_instance(self):
        
        cap = cv2.VideoCapture(0)
        
        # check if the webcam is openable 
        if not cap.isOpened():
            return None 
        
        return cap 
    
    
    def get_picture(self, hsv_convert=True):
        _, frame = self.camera.read()
        # height, width, channels = frame.shape
        # # add a black bar to ensure contours
        # frame = cv2.rectangle(frame, (width-10,0), (width,height), (0,0,0), -1)
        hsv = None 
        if(hsv_convert == True):
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
        return frame, hsv


    def get_picture_from_file(self, image, hsv_convert=True):
        frame = cv2.imread(image)
        # height, width, channels = frame.shape
        # # add a black bar to ensure contours
        # frame = cv2.rectangle(frame, (width-10,0), (width,height), (0,0,0), -1)
        hsv = None 
        if(hsv_convert == True):
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
        return frame, hsv       
    
    def release_camera(self):
        try:
            self.camera.release()
        except:
            print("Could not release camera")
        

        
        

