import tensorflow as tf
import numpy as np
from matplotlib import pyplot as plt
import cv2
from time import time
from PIL import ImageGrab
import math
import random
"""
from multiprocessing import Process
from socket import SocketIO
from hashlib import new
from threading import Thread, Timer, Lock
"""

import paho.mqtt.client as mqtt
from threading import Thread
from stmpy import Machine, Driver
import ipywidgets as widgets
from IPython.display import display

class Level:
    def __init__(self, name, cap, tr, bl):
        self.name = name
        self.cap = cap
        self.tr = tr
        self.bl = bl
        self.line_thickness = 2

    def getWindowWidth(self):
        return int(self.cap.get(3))
        
    def getWindowHeight(self):
        return int(self.cap.get(4))

    def isPointWithinBoundaries(self, p):
        if(self.bl[0]>self.tr[0]):
            smallestX = self.tr[0]
            biggestX = self.bl[0]
        else:
            smallestX = self.bl[0]
            biggestX = self.tr[0]
            
        if(self.bl[1]>self.tr[1]):
            smallestY = self.tr[1]
            biggestY = self.bl[1]
        else:
            smallestY = self.bl[1]
            biggestY = self.tr[1]
            
        if(p[0] in range (smallestX, biggestX) and p[1] in range (smallestY, biggestY)):
            return True
        return False
    
    def isPersonWitihinBoundaries(self, joint_points):
        for point in joint_points:
            if(not self.isPointWithinBoundaries(point)):
                # Red color in BGR
                return False
        return True
    
    def toString(self):
        print("This is", self.name)
        
        
    def calculatePoints(self, joint_points):
        if(self.isPersonWitihinBoundaries(joint_points)):
            return 1
        else: 
            return 0
    
    def draw(self, frame, joint_points):
        color = (0, 255, 0)
        if(not self.isPersonWitihinBoundaries(joint_points)):
            # Red color in BGR
            color = (0, 0, 255)
        cv2.rectangle(frame, self.bl, self.tr, color, thickness=self.line_thickness)
    
class Game:
    def __init__(self, precision):
        self.precision = precision
        self.cap = cv2.VideoCapture(0)
        self.window_width = int(self.cap.get(3))
        self.window_height = int(self.cap.get(4))
        
        bl_level_one = [int(self.window_width / 5), self.window_height]
        tr_level_one = [int((self.window_width / 5) * 2), 0]
        self.level_one = Level("Level 1", self.cap, tr_level_one, bl_level_one)
        
        tr_level_two = [self.window_width, int(self.window_height / 9)]
        bl_level_two = [0, int((self.window_height / 9) * 8)]
        self.level_two = Level("Level 2", self.cap, tr_level_two, bl_level_two)
        
        bl_level_three = [int(self.window_width / 3), self.window_height]
        tr_level_three = [int((self.window_width / 3) * 2), int(self.window_height / 2)]
        self.level_three = Level("Level 3", self.cap, tr_level_three, bl_level_three)
        
        self.levels = [self.level_one, self.level_two, self.level_three]
        
        self.interpreter = tf.lite.Interpreter(model_path='game/lite-model_movenet_singlepose_lightning_3.tflite')
        self.interpreter.allocate_tensors()
        
        self.window_width = int(self.cap.get(3))
        self.window_height = int(self.cap.get(4))
        self.line_thickness = 2
        self.color = (0, 255, 255)
        self.current_level = 1
        self.score = 0
        self.generateRandomLevels(10)
        
    def generateRandomLevels(self, amount):
        for x in range(0, amount):
            ran_x1 = random.randint(0, self.window_width)
            ran_y1 = random.randint(0, self.window_height)
            bl = [ran_x1, ran_y1]
            if(ran_x1 > int(self.window_width/2)):
                ran_x2 = ran_x1 - random.randint(int(self.window_width/3), self.window_width)
            else:
                ran_x2 = ran_x1 + random.randint(int(self.window_width/3), self.window_width)
                
            if(ran_y1 > int(self.window_height/2)):
                ran_y2 = ran_y1 - random.randint(int(self.window_height/3), self.window_height)
            else:
                ran_y2 = ran_y1 + random.randint(int(self.window_height/3), self.window_height)

            tr = [ran_x2, ran_y2]
            self.levels.append(Level("Level " + str(x + 4), self.cap, tr, bl))
          
            
    def draw_keypoints(self, frame, keypoints, confidence_threshold):
        y, x, c = frame.shape
        shaped = np.squeeze(np.multiply(keypoints, [y,x,1]))

        for kp in shaped:
            ky, kx, kp_conf = kp
            if kp_conf > confidence_threshold:
                cv2.circle(frame, (int(kx), int(ky)), 4, (0,255,0), -1) 
                
    
    def getJointPoints(self, frame, keypoints_with_scores):
        joint_points = []
        
        y, x, c = frame.shape
        shaped = np.squeeze(np.multiply(keypoints_with_scores, [y,x,1]))

        for kp in shaped:
            ky, kx, kp_conf = kp
            if kp_conf > self.precision:
                joint_points.append([int(kx), int(ky)])
        
        return joint_points
        
    
    def drawLevels(self, frame, keypoints_with_scores):    
        joint_points = self.getJointPoints(frame, keypoints_with_scores)
        self.levels[self.current_level - 1].draw(frame, joint_points) 

    def draw_countdown(self, frame, time):
        font = cv2.FONT_HERSHEY_SIMPLEX
        line = cv2.LINE_4
        countdown = 5 - math.floor(time)
        countdownStr = str(countdown)
        if(time >= 4.9):
            countdownStr = ""

        cv2.putText(frame, countdownStr, (int(self.window_width / 2), int(self.window_height / 2)), font, 8, (255, 0, 0), 2, line)

        
    def updateScore(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        coordinates = "Score: " + str(self.score)
        cv2.putText(frame, coordinates, (50, 50), font, 1, (255, 0, 0), 2, cv2.LINE_4)
    
    def incrementLevel(self, frame, joint_points):
        self.score += self.levels[self.current_level - 1].calculatePoints(joint_points)           
        self.current_level += 1
        
    
    def start(self, callback):
        print("-----Starting Game-----")
        previous = time()
        delta = 0
        rounds_played = 1

        #while self.current_level <= len(self.levels):
        while False:
            ret, frame = self.cap.read()
            # Reshape image
            frame = cv2.flip(frame, 1)
            img = frame.copy()
            img = tf.image.resize_with_pad(np.expand_dims(img, axis=0), 192,192)
            input_image = tf.cast(img, dtype=tf.float32)

            # Setup input and output
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()

            # Make predictions
            self.interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
            self.interpreter.invoke()
            keypoints_with_scores = self.interpreter.get_tensor(output_details[0]['index'])
            
            current = time()
            delta += current - previous
            previous = current


            # ------ Rendering ------
            self.updateScore(frame)
            self.draw_keypoints(frame, keypoints_with_scores, self.precision)
            self.draw_countdown(frame, delta)
            self.drawLevels(frame, keypoints_with_scores)
            
                        # ------ Next round controller ------
            if delta > 5:
                cv2.imwrite(f'images/{self.current_level}.png', frame)
                joint_points = self.getJointPoints(frame, keypoints_with_scores)
                
                self.incrementLevel(frame, joint_points)
                # Reset the time' counter
                delta = 0

            
            cv2.imshow('Hole in the wall!', frame)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                break
        
        callback(self.score)
        cv2.destroyAllWindows()
        self.cap.release()   