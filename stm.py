from stmpy import Driver, Machine
import paho.mqtt.client as mqtt
from threading import Thread
import socket
import time
#import gpiozero
#import movenet as mn
import keyboard as kb
import sys
from pyvoice import client, server
from pyvoice import stopthread as st

print("Hello, World!")
p1_topic = "ttm4115/team06/HITW/user1"
p2_topic = "ttm4115/team06/HITW/user2"
ctrl_topic = "ttm4115/team06/HITW/controller"

voiceport = 55099

class HoleInTheWall:
    def __init__(self):
        
        self.led = None
        #self.button = gpiozero.Button(1)
        #self.led = gpiozero.LED(1)
        #self.greenLightOn = self.led.on
        #self.greenLightOff = self.led.off
        self.own_score = 0
        self.round_number = 0

    def on_button_press(self):
        print("asd")
        #self.stm.send('button1')

    def kb_backup(self):
        kb.add_hotkey("numpad_enter", self.on_button_press())

    def terminateSession(self):
        print("Terminate session")
        myclient.unsubscribe(p1_topic)
        myclient.unsubscribe(p2_topic)

        try:
            voiceserver_thread.stop()
        except:
            pass

        voiceclient_thread.stop()

    def sendGameInvite(self): #subscribe to player 2
        myclient.subscribe(p2_topic)

        myclient.unsubscribe(ctrl_topic)
        myclient.publish(ctrl_topic, "receiveGreenLight")
        myclient.subscribe(ctrl_topic)

    def startGameSession(self):
        voiceip = socket.gethostbyname(socket.gethostname())
        global voiceserver_thread; global voiceclient_thread
        voiceserver_thread = st.StoppableThread(target = createVoiceServer(voiceport)).start()
        voiceclient_thread = st.StoppableThread(target = createVoiceClient(voiceip, voiceport)).start()
        #TODO: MQTT Communicate Voice IP

    def startGame(self):
        score = [None, None, None]
        print("c")
        #movenet_detector = mn.MoveNet()

    def startRound(self):
        print("startRound")
    
    def showTotalScores(self):
        print("show total scores")
    
    def sendScore(self):
        print("Send Score")

    def greenLight(self):
        if self.led != None:
            self.led.on
        else:
            print("Lights on!")

    def lightsOff(self):
        if self.led != None:
            self.led.off
        else:
            print("Lights Off")

    def sendGameInvite(self):
        myclient.publish(p2_topic, "receiveGameInvite")

    def sendInviteTimedOut(self):
        myclient.publish(p2_topic, "receiveInviteTimedOut")

    def sendInviteAccepted(self): #TODO: Implement correct IP parsing from MQTT
        myclient.publish(p1_topic, "inviteAccepted")
        myclient.subscribe(p1_topic)
        voiceclient2_thread = st.StoppableThread(target = createVoiceClient(voiceip, voiceport)).start()

    def terminateGameSession(self):
        voiceserver_thread.stop()
        voiceclient_thread.stop()
        voiceserver_thread.join()
        voiceclient_thread.join()
        print("asd")

    def endGame(self):
        print("asd")

t0 = {'source': 'initial',
      'target': 'idle',
      'effect': 'kb_backup'}

# Change 1: effect is removed
t1 = {'trigger': 'button1', #button1
      'source': 'idle',
      'target': 'connecting'}

# Change 2: effect is removed here, too
t2 = {'trigger': 't', #timer
      'source': 'connecting',
      'target': 'idle',
      'effect': 'sendInviteTimedOut'}

t3 = {'trigger': 'inviteAccepted', #inviteAccepted
      'source': 'connecting',
      'target': 'initializeGame'}

t4 = {'trigger': 'round1',  #round1
      'source': 'initializeGame',
      'target': 'playing'}

t5 = {'trigger': 'newRound', #newRound
      'effect' : 'sendScore',
      'source': 'playing',
      'target': 'playing'}

t6 = {'trigger': 'gameFinished', #gameFinished
      'source': 'playing',
      'target': 'postGame'}

t7 = {'trigger': 'doubleClick',    #doubleClick
      'source': 'postGame',
      'target': 'initializeGame'}

t8 = {'trigger': 'button2',    #button2
      'source': 'playing',
      'target': 'idle',
      'effect': 'endGame'}

t9 = {'trigger': 'button3',    #button3
      'source': 'postGame',
      'target': 'idle'}

t10 = {'trigger': 'recieveGameInvite', #receiveGreenLight
      'source': 'idle',
      'target': 'waitingToAccept'}

t11 = {'trigger': 'receiveInviteTimedOut', #receiveInviteTimedOut
      'source': 'waitingToAccept',
      'target': 'idle'}

t12 = {'trigger': 'button1', #p2 accept game
      'source': 'waitingToAccept',
      'target': 'initializeGame',
      'effect': 'sendInviteAccepted'}

# Change 3: We declare dicts for the states
idle = {'name': 'idle',
        'entry': 'terminateGameSession; lightsOff;'
        }

connecting = {'name': 'connecting',
              'entry': 'sendGameInvite; start_timer("t", 60000); startGameSession; sendGreenLight'
              }

waitingToAccept = {'name': 'waitingToAccept',
                   'entry': 'greenLight; start_timer("t", 1000)',
                   }

initializeGame = {'name': 'initializeGame',
           'entry': 'startGame; start_timer("t", 1000); startPoseNetTracker; greenLight'
           }

playing = {'name': 'playing',
           'entry': 'startRound;'
           }

postGame = {'name': 'postGame',
            'entry': 'showScores; start_timer("t", 1000), endGame; lightsOff'
            }

class MQTT_Client_1:
    def __init__(self):
        self.count = 0
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        #self.stm_driver.send("message", "tick_tock")
        print(msg.payload.decode("utf-8"))
        rcvd_msg = msg.payload.decode("utf-8")
        #self.stm_driver.send(msg.payload.decode("utf-8"), "quiz")
        #self.client.publish("gruppe6/quiz/question", "Quiz?")
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
    while True:
        if voiceclient_thread.stopped():
            voice_client.terminate_client()

def createVoiceServer(port):
    server_client = server.Server(port)
    while True:
        if voiceserver_thread.stopped():
            server_client.terminate_server()

broker, port = "mqtt.item.ntnu.no", 1883

player = HoleInTheWall()
player_machine = Machine(transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12], states=[
                         idle, connecting, waitingToAccept, playing, postGame], obj=player, name="player")
#hitw_functions = [attribute for attribute in dir(HoleInTheWall) if callable(getattr(HoleInTheWall, attribute)) if attribute.startswith("__") is False].replace('"', '')
player.stm = player_machine

driver = Driver()
driver.add_machine(player_machine)

myclient = MQTT_Client_1()
player.mqtt_client = myclient.client
myclient.stm_driver = driver

driver.start()
myclient.start(broker, port)

#def game(mqttclient, player):
#    clock = time.Clock()
#    roundno = 0
#    running = True
#    while running:

#Fallback Keyboard input
