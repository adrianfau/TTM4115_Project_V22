import tensorflow as tf
import numpy as np
from matplotlib import pyplot as plt
import cv2
from time import time
from threading import Thread, Timer, Lock
from multiprocessing import Process
import math
import random
from hashlib import new
from socket import SocketIO
from stmpy import Driver, Machine
import paho.mqtt.client as mqtt
from threading import Thread
from stmpy import Machine, Driver
import ipywidgets as widgets
from IPython.display import display
import stoppablethread as st
from pyvoice import client, server
import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import os, glob

class Slideshow:
    def __init__(self, width, height, interval, amountOfLevels):
        self.height = height
        self.width = width
        self.interval = interval
        self.amountOfPictures = amountOfLevels * 2
        
        # Window adjustments
        self.root=tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")

        # Images to be loaded
        self.images=[]
        
        # Add images that exist in folder
        for img_index in range(1, self.amountOfPictures):
            try:
                self.images.append(ImageTk.PhotoImage(Image.open(f"images/output_{img_index}.png")))
            except:
                print(f"IGNORING: images/output_{img_index}.png does not exist")

        self.l=Label()
        self.l.pack()

        # Keep track of images that are shown
        self.x = 0

    # Change to next image
    def move(self):
        if self.x == self.amountOfPictures:
            self.root.destroy()
            for filename in glob.glob("images"):
                if ("green" not in str(filename).lower()) or ("store" not in str(filename).lower()):
                    os.remove(filename)
            return
        
        #Check if image exist in list
        if(self.x < len(self.images)):
            self.l.config(image=self.images[self.x])
        
        self.x = self.x+1
        
        # Recursive call to slide to next image
        self.root.after(self.interval, self.move)
    
    def start_slideshow(self):
        self.move()
        self.root.mainloop()

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
    
    def isPersonWithinBoundaries(self, joint_points):
        for point in joint_points:
            if(not self.isPointWithinBoundaries(point)):
                # Red color in BGR
                return False
        return True
    
    def toString(self):
        print("This is", self.name)
        
    def calculatePoints(self, joint_points):
        if(self.isPersonWithinBoundaries(joint_points)):
            return 1
        else: 
            return 0
    
    def draw(self, frame, joint_points):
        color = (0, 255, 0)
        if(not self.isPersonWithinBoundaries(joint_points)):
            # Red color in BGR
            color = (0, 0, 255)
        cv2.rectangle(frame, (int(self.bl[0]), int(self.bl[1])), (int(self.tr[0]), int(self.tr[1])), color, thickness=self.line_thickness)
    
class Game:
    def __init__(self, precision, amountOfLevels):
        self.precision = precision
        self.cap = cv2.VideoCapture(0)
        self.window_width = int(self.cap.get(3))
        self.window_height = int(self.cap.get(4))
        self.amountOfLevels = amountOfLevels
        
        self.levels = []
        
        self.interpreter = tf.lite.Interpreter(model_path='game/lite-model_movenet_singlepose_lightning_3.tflite')
        self.interpreter.allocate_tensors()
        
        self.window_width = int(self.cap.get(3))
        self.window_height = int(self.cap.get(4))
        self.line_thickness = 2
        self.color = (0, 255, 255)
        self.current_level = 1
        self.score = 0
        self.generateRandomLevels()
        
    def generateRandomLevels(self):
        for x in range(0, self.amountOfLevels):
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

        while self.current_level <= len(self.levels):
        #while False:
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

voiceport = 10505           #For connection to remotely hosted voice server
voiceip = "185.71.211.252"  #IP of server hosted on home computer

active_player = None
downloaded_images = 0

class HoleInTheWall:
    
    def load_images(self):
        self.green_on = open("images/green_on.png", "rb").read()
        self.green_off = open("images/green_off.png", "rb").read()
    
    def publishController(self, trigger, message):
        player.mqtt_client.unsubscribe(self.channel)
        player_machine.send(trigger)
        player.mqtt_client.publish(self.channel, message)
        player.mqtt_client.subscribe(self.channel)
        
    def sendInvite(self, b):
        self.publishController("button", "receivedGameInvite")
    
    def sendRematch(self, b):
        self.publishController("rematch", "rematch")
        
    def sendQuit(self, b):
        self.publishController("quit", "quit")
        
    def sendInviteAccepted(self, b):
        self.publishController("sendInviteAccepted", "inviteAccepted")
        voiceclient_thread = st.StoppableThread(target = createVoiceClient, args=(voiceip, voiceport,)).start()
        
    def display(self):
        self.button_switch = widgets.Button(description="Invite")
        self.button_switch.on_click(self.sendInvite)
        self.button_accept = widgets.Button(description="Accept")
        self.button_accept.on_click(self.sendInviteAccepted)
        self.button_rematch = widgets.Button(description="Rematch")
        self.button_rematch.on_click(self.sendRematch)
        self.button_quit = widgets.Button(description="Quit")
        self.button_quit.on_click(self.sendQuit)
        self.green = widgets.Image(value=self.green_off, format='png', width=50, height=50)
        display(self.green, self.button_switch, self.button_rematch, self.button_quit, self.button_accept)
    
    def hideAcceptbutton(self):
        self.button_accept.layout.display = "none"
    def hideRematchbutton(self):
        print()
    def hideQuitbutton(self):
        print()
    
    def showButtons(self,buttons):
        self.button_switch.layout.display = "none"
        self.button_accept.layout.display = "none"
        self.button_rematch.layout.display = "none"
        self.button_quit.layout.display = "none"
        for x in buttons:
            x.layout.display = "block"
    
    def __init__(self):
        self.own_score = 0
        self.round_number = 0
        self.load_images()
        self.display()
        self.amountOfLevels = 15
        self.game = Game(0.1, self.amountOfLevels)
        self.channel = "team6/test"
        
    def terminateSession(self):
        self.showButtons([self.button_switch])
        active_player = None
        self.listenOnChannel()
        global downloaded_image
        downloaded_image = 0
        try:
            voiceclient.terminate_client()
            print("Ending Voice Channel")
            try:
                voiceclient_thread.stop()
                voiceclient_thread.terminate_client()
                voiceclient_thread.join()
            except:
                pass
        except:
            pass

    def startGameSession(self):
        global voiceclient_thread #Creates voice client thread and initiates active player status
        voiceclient_thread = st.StoppableThread(target = createVoiceClient, args=(voiceip, voiceport,)).start()
        active_player = "PLAYER_1"
        self.listenOnChannel()
        print("IS PLAYER 1")
    
    def quitGame(self, score):
        print("SCORE: ", score)
        player_machine.send("gameFinished")
        
    def sendImages(self):
        print("Sending images")
        for img_index in range(1, self.amountOfLevels + 1):
            try: 
                f=open(f"images/{img_index}.png", "rb") #3.7kiB in same folder
                fileContent = f.read()
                byteArr = bytearray(fileContent)
                player.mqtt_client.publish(self.channel, byteArr)
            except KeyboardInterrupt:
                print("Could not send image")
        
    def receivedImage(self):
        # more callbacks, etc
        # Create a file with write byte permission
        f = open('images/output.png', "wb")
        f.write(msg.payload)
        #print("Image Received")
        f.close()

    def startGame(self):
        self.showButtons([self.button_quit])
        self.game.start(self.quitGame)

    def greenLight(self):
        self.showButtons([self.button_accept])
        self.green.set_trait(name='value', value=self.green_on)

    def lightsOff(self):
        self.green.set_trait(name='value', value=self.green_off)

    def sendGreenLight(self):
        self.green.set_trait(name='value', value=self.green_on)

    def sendGameInvite(self):
        self.showButtons([])
        #print("Send Game Invite")
        player.mqtt_client.publish("team6/gameInvite", "gameInvite")

    def inviteTimedOut(self):
        print("Send invite timed out")
        active_player = None

    def receiveInviteTimedOut(self):
        print("Receive Invite Timed Out")

    def visConnecting(self):
        print("------In Connecting------")
    
    def visIdle(self):
        print("------In Idle------")
    
    def visWaitingToAccept(self):
        print("------WaitingToAccept------")
        active_player = "PLAYER_2"
        self.listenOnChannel()
        print("IS PLAYER 2")

    def visInitilizeGame(self):
        print("------Initilize Game------")
        
    def showPostGame(self):
        print("-----In PostGame-----")
        self.showButtons([self.button_rematch, self.button_quit])
        
    def listenOnChannel(self):
        if(active_player == "PLAYER_2"):
            self.channel = "team6/PLAYER_1"
            return
        elif(active_player == "PLAYER_1"):
            self.channel = "team6/PLAYER_2"
            return
        self.channel = "team6/test"


#---------Transitions---------#
t0 = {'source': 'initial',
      'target': 'idle'}

t1 = {'trigger': 'button',
      'source': 'idle',
      'target': 'connecting'}

t2 = {'trigger': 't',
      'source': 'connecting',
      'target': 'idle',
      'effect': 'sendInviteTimedOut'}

t3 = {'trigger': 'inviteAccepted',
      'source': 'connecting',
      'target': 'initializeGame'}

t4 = {'trigger': 'gameFinished',
      'source': 'initializeGame',
      'target': 'postGame'}

t5 = {'trigger': 'rematch',
      'source': 'postGame',
      'target': 'initializeGame'}

t6 = {'trigger': 'quit',
      'source': 'postGame',
      'target': 'idle'}

t7 = {'trigger': 'receivedGameInvite', 
      'source': 'idle',
      'target': 'waitingToAccept'}

t8 = {'trigger': 'receiveInviteTimedOut',
      'source': 'waitingToAccept',
      'target': 'idle'}

t9 = {'trigger': 't',
      'source': 'waitingToAccept',
      'target': 'idle'}

t10 = {'trigger': 'sendInviteAccepted',
      'source': 'waitingToAccept',
      'target': 'initializeGame'}

#---------States---------#
idle = {'name': 'idle',
        'entry':'visIdle; terminateSession;'
        }

connecting = {'name': 'connecting',
              'entry': 'visConnecting; sendGameInvite; start_timer("t", 10000); startGameSession; sendGreenLight'
              }

waitingToAccept = {'name': 'waitingToAccept',
                   'entry': 'visWaitingToAccept; greenLight; start_timer("t", 10000)'
                   }

initializeGame = {'name': 'initializeGame',
           'entry': 'visInitilizeGame; startGame; greenLight'
           }

postGame = {'name': 'postGame',
            'entry': 'showPostGame; sendImages; lightsOff'
            }

def createVoiceClient(target_ip, target_port):
    global voiceclient
    voiceclient = client.Client(target_ip, target_port)

#---------MQTT Client Logic---------
class MQTT_Client_1:
    
    def __init__(self, downloaded_images):
        self.count = 0
        self.downloaded_images = downloaded_images
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))
        print("Running...")

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        if self.downloaded_images > 1 and self.downloaded_images % 29 == 0: #Logic to handle starting the slideshow
            print("Starting slideshow")
            slideshow = Slideshow(1280, 720, 1000, 15)
            slideshow.start_slideshow()
            self.downloaded_images = 0
        
        if (len(msg.payload) > 50): #Logic to handle incoming images
            #print("Image Received")
            # more callbacks, etc
            # Create a file with write byte permission
            f = open(f'images/output_{self.downloaded_images}.png', "wb")
            f.write(msg.payload)
            f.close()
            self.downloaded_images += 1
            return
        rcvd_msg = msg.payload.decode("utf-8") #Else: send payload as message to state machine
        self.stm_driver.send(rcvd_msg, "player")
            

    def start(self, broker, port):
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)
        self.client.subscribe("team6/test")
        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

broker, port = "mqtt.item.ntnu.no", 1883

player = HoleInTheWall()
player_machine = Machine(transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10], states=[
                         idle, connecting, waitingToAccept, postGame, initializeGame], obj=player, name="player")

driver = Driver()
driver.add_machine(player_machine)

myclient = MQTT_Client_1(downloaded_images)
player.mqtt_client = myclient.client
myclient.stm_driver = driver

driver.start()
myclient.start(broker, port)