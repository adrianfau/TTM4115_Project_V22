#import tensorflow as tf
#import tensorflow-gpu
from stmpy import Driver, Machine
import paho.mqtt.client as mqtt
#from PIL import ImageGrab
#import keyboard as kb
from threading import Thread, Timer, Lock
import ipywidgets as widgets
import socket
import time
import sys
#from multiprocessing import Process
#from hashlib import new
#from socket import SocketIO
#import cv2

from pyvoice import client, server
import ipywidgets as widgets
from IPython.display import display
import stoppablethread as st
from game import Game, Level

print("Hello, World!")
p1_topic = "ttm4115/team06/HITW/user1"
p2_topic = "ttm4115/team06/HITW/user2"
ctrl_topic = "ttm4115/team06/HITW/controller"

voiceport = 10505
voiceip = "185.71.211.252"
active_player = None
downloaded_images = 0
""""
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
"""
class HoleInTheWall:
    def load_images(self):
        self.green_on = open("images/green_on.png", "rb").read()
        self.green_off = open("images/green_off.png", "rb").read()
    
    def publishController(self, trigger, message):
        player.mqtt_client.unsubscribe(self.channel)
        player_machine.send(trigger)
        player.mqtt_client.publish(self.channel, message)
        player.mqtt_client.subscribe(self.channel)
    
    def display(self):
        self.button_switch = widgets.Button(description="Invite")
        self.button_switch.on_click(self.sendInvite)
        self.button_accept = widgets.Button(description="Accept")
        self.button_accept.on_click(self.sendInviteAccepted123)
        self.button_rematch = widgets.Button(description="Rematch")
        self.button_rematch.on_click(self.sendRematch)
        self.button_quit = widgets.Button(description="Quit")
        self.button_quit.on_click(self.sendQuit)
        #self.button_next = widgets.Button(description="DubleClick")
        #self.button_next.on_click(self.on_button_switch)
        self.green = widgets.Image(value=self.green_off, format='png', width=50, height=50)
        display(self.green, self.button_switch, self.button_rematch, self.button_quit, self.button_accept)
    
    def __init__(self):
        self.load_images()
        self.display()
        self.game = Game(0.1)
        self.channel = "team6/test"

    def terminateSession(self):
        print("terminateSession")
        if voiceclient_thread != None:
            print("Ending Voice Channel")
            try:
                voiceclient_thread.stop()
            except:
                pass
            if voiceclient_thread.stopped():
                #voiceserver_thread.terminate_server()
                voiceclient_thread.terminate_client()
                voiceclient_thread.join()
                #voiceserver_thread.join()
    
    def startGameSession(self):
        print("Starting Game session - Create Voice Channel")
        global voiceclient_thread #global voiceip
        #voiceip = socket.gethostbyname(socket.gethostname())
        #voiceserver_thread = st.StoppableThread(target = createVoiceServer, args=(voiceport,)).start()
        voiceclient_thread = st.StoppableThread(target = createVoiceClient, args=(voiceip, voiceport,)).start()
        #myclient.publish(f"{voiceip}")
        #TODO: MQTT Communicate Voice IP

    def sendImages(self):
        print("Sending images")
        
        f=open("images/red_on.png", "rb") #3.7kiB in same folder
        fileContent = f.read()
        byteArr = bytearray(fileContent)

        player.mqtt_client.publish(self.channel, byteArr)

    def receivedImage(self):
        # more callbacks, etc
        # Create a file with write byte permission
        f = open('images/output.png', "wb")
        f.write(msg.payload)
        print("Image Received")
        f.close()

    def sendInvite(self, b):
        self.publishController("button", "receivedGameInvite")
    
    def sendRematch(self, b):
        self.publishController("rematch", "rematch")
        
    def sendQuit(self, b):
        self.publishController("quit", "quit")
        
    def sendInviteAccepted123(self, b):
        self.publishController("sendInviteAccepted", "inviteAccepted")
        voiceclient_thread = st.StoppableThread(target = createVoiceClient, args=(voiceip, voiceport,)).start()

    def startGame(self):
        print("startGame")
        self.game.start(self.quitGame)
        self.sendImages()

    def sendGameInvite(self): #subscribe to player 2
        print("send game invite")
        player.mqtt_client.publish("team6/gameInvite", "gameInvite")
        
    def startRound(self):
        print("startRound")
    
    def showTotalScores(self):
        print("Show total scores")
    
    def sendScore(self):
        print("Send Score")

    def greenLight(self):
        print("Green light")
        #self.led.on
        self.green.set_trait(name='value', value=self.green_on)

    def lightsOff(self):
        print("Lights off")
        #self.led.off
        self.green.set_trait(name='value', value=self.green_off)

    def sendGreenLight(self):
        #player.mqtt_client.publish("team6/greenLight", "greenlight")
        print("send green light")
        self.green.set_trait(name='value', value=self.green_on)
        
    def sendInviteTimedOut(self):
        print("send invite timed out")
        #player.mqtt_client.publish("team6/timeOut", "Invite timed out")
        active_player = None

    def sendScore(self):
        print("Sender score")
        self.score += 1
        #player.mqtt_client.publish("team6/scores", self.score)
        # --------Vise bilder til motpart-------- #
        # player.mqtt_client.publish("team6/scores", self.picture)

    def startPoseNetTracker(self):
        print("starting poseNetTracker")

    def showTotalScores(self):
        print("Show total score")
        #player.mqtt_client.publish("team6/scores", self.score)
                                   
    def endGame(self):
        print("Ending game")
    
    def visState2(self):
        print("------In state 2------")
        active_player = "PLAYER_1"
        self.listenOnChannel()
        print("IS PLAYER 1")
    
    def visIdle(self):
        print("------In Idle------")
        active_player = None
        self.listenOnChannel()
        global downloaded_image
        downloaded_image = 0
    
    def visWaitingToAccept(self):
        print("------WaitingToAccept------")
        active_player = "PLAYER_2"
        self.listenOnChannel()
        print("IS PLAYER 2")

    def visInitilizeGame(self):
        print("------InitilizeGame------")
        
    def showPostGame(self):
        print("-----In PostGame-----")
        
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

"""
t4 = {'trigger': 'round1',
      'source': 'initializeGame',
      'target': 'playing'}
"""

"""t5 = {'trigger': 'newRound',
      'source': 'playing',
      'target': 'playing',
      'effect': 'sendScore'}"""

t6 = {'trigger': 'gameFinished',
      'source': 'initializeGame',
      'target': 'postGame'}

t7 = {'trigger': 'rematch',
      'source': 'postGame',
      'target': 'initializeGame'}

"""t8 = {'trigger': 'button',
      'source': 'initializeGame',
      'target': 'postGame'}"""

t9 = {'trigger': 'quit',
      'source': 'postGame',
      'target': 'idle'}

t10 = {'trigger': 'receivedGameInvite', 
      'source': 'idle',
      'target': 'waitingToAccept'}

t11 = {'trigger': 'receiveInviteTimedOut',
      'source': 'waitingToAccept',
      'target': 'idle'}

t12 = {'trigger': 't',
      'source': 'waitingToAccept',
      'target': 'idle'}

t13 = {'trigger': 'sendInviteAccepted',
      'source': 'waitingToAccept',
      'target': 'initializeGame'}

#---------States---------#
idle = {'name': 'idle',
        'entry':'visIdle;lightsOff;terminateSession;'
        }

connecting = {'name': 'connecting',
              'entry': 'visState2; sendGameInvite; start_timer("t", 10000); startGameSession; sendGreenLight'
              }

waitingToAccept = {'name': 'waitingToAccept',
                   'entry': 'visWaitingToAccept; becomePlayer2; greenLight; start_timer("t", 10000)'
                   }

initializeGame = {'name': 'initializeGame',
           'entry': 'visInitilizeGame; startGame; start_timer("t", 10000); startPoseNetTracker; greenLight'
           }

playing = {'name': 'playing',
           'entry': 'startRound'
           }

postGame = {'name': 'postGame',
            'entry': 'showTotalScores; showPostGame; start_timer("t", 10000); endGame; lightsOff'
            }

class MQTT_Client_1:
    def __init__(self):
        self.count = 0
        self.downloaded_images = 0
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        print(msg.payload.decode("utf-8"))
        if (len(msg.payload) > 50):
            print("Image Received")
            # more callbacks, etc
            # Create a file with write byte permission
            f = open(f'images/output_{downloaded_images}.png', "wb")
            f.write(msg.payload)
            f.close()
            self.downloaded_images += 1
            return
        rcvd_msg = msg.payload.decode("utf-8")
        self.stm_driver.send(rcvd_msg, "player")

    def start(self, broker, port):
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)
        self.client.subscribe(ctrl_topic)
        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

def createVoiceClient(target_ip, target_port):
    voice_client = client.Client(target_ip, target_port)

broker, port = "mqtt.item.ntnu.no", 1883

player = HoleInTheWall()
player_machine = Machine(transitions=[t0, t1, t2, t3, t6, t7, t9, t10, t11, t12, t13], states=[
                         idle, connecting, waitingToAccept, playing, postGame, initializeGame], obj=player, name="player")

driver = Driver()
driver.add_machine(player_machine)

myclient = MQTT_Client_1()
player.mqtt_client = myclient.client
myclient.stm_driver = driver

driver.start()
myclient.start(broker, port)