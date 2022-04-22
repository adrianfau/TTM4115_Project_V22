from stmpy import Driver, Machine
import paho.mqtt.client as mqtt
from threading import Thread
import gpiozero as gz
import movenet as mn

print("Hello, World!")
user1_topic = "ttm4115/team06/HITW/user1"
user2_topic = "ttm4115/team06/HITW/user2"
ctrl_topic = "ttm4115/team06/HITW/controller"


class HoleInTheWall:
    def __init__(self):
       # self.button = gz.Button(1)
       # self.led = gz.LED(1)
       # self.greenLightOn = self.led.on
       # self.greenLightOff = self.led.off
        self.own_score = 0
       # self.round_number = 0

    def on_button_press(self, b):
        self.stm.send('button1')

    def terminateSession():
        print("Terminate session")

    def startGameSession():
        print("b")

    def startGame():
        print("c")
        movenet_detector = mv.MoveNet()
    
    def startPoseNetTracker():
        print("Start PoseNetTracker")

    def startRound():
        print("startRound")

    def showScores():
        print("d")
    
    def showTotalScores():
        print("show total scores")
    
    def sendScore():
        print("Send Score")

    def waitingToAccept():
        print("e")

    def greenLight():
        print("greenLight")

    def lightsOff():
        print("lights off")


    def sendGreenLight():
        myclient.publish(user2_topic, "greenlight")

    def sendGameInvite():
        myclient.publish(user2_topic, "gameinvite")

    def sendInviteTimedOut():
        myclient.publish(user2_topic, "")

    def receiveInviteTimedOut():
        self.led.on

    def receiveGreenLight():
        print("asd")

    def endGame():
        print("asd")


t0 = {'source': 'initial',
      'target': 'idle'}

# Change 1: effect is removed
button1 = {'trigger': 'button1',
      'source': 'idle',
      'target': 'connecting'}

# Change 2: effect is removed here, too
t = {'trigger': 't',
      'source': 'connecting',
      'target': 'idle'}

inviteAccepted = {'trigger': 'inviteAccepted',
      'source': 'connecting',
      'target': 'initializeGame'}

round1 = {'trigger': 'round1',
      'source': 'initializeGame',
      'target': 'playing'}

newRound = {'trigger': 'newRound',
      'effect' : 'sendScore',
      'source': 'playing',
      'target': 'playing'}

gameFinished = {'trigger': 'gameFinished',
      'source': 'playing',
      'target': 'postGame'}

doubleClick = {'trigger': 'doubleClick',
      'source': 'postGame',
      'target': 'initializeGame'}

button2 = {'trigger': 'button2',
      'source': 'playing',
      'target': 'idle'}    

button3 = {'trigger': 'button3',
      'source': 'postGame',
      'target': 'idle'}


recieveGreenLight = {'trigger': 'recieveGreenLight',
      'source': 'idle',
      'target': 'waitingToAccept'}

recieveInviteTimedOut = {'trigger': 'receiveInviteTimedOut',
      'source': 'waitingToAccept',
      'target': 'idle'}

button4 = {'trigger': 'button1',
      'source': 'waitingToAccept',
      'target': 'initializeGame'}

# Change 3: We declare dicts for the states
idle = {'name': 'idle',
        'entry': 'terminateGameSession; start_timer("t", 60000); lightsOff;'
        }

connecting = {'name': 'connecting',
              'entry': 'sendGameInvite; start_timer("t", 60000); startGameSession; sendGreenLight'
              }

waitingToAccept = {'name': 'waitingToAccept',
                   'entry': 'greenLight; start_timer("t", 1000)'
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
        self.stm_driver.send(msg.payload.decode("utf-8"), "quiz")
        #self.client.publish("gruppe6/quiz/question", "Quiz?")

    def start(self, broker, port):

        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)
        self.client.subscribe("gruppe6/quiz/answer")

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()


broker, port = "mqtt.item.ntnu.no", 1883

player = HoleInTheWall()
player_machine = Machine(transitions=[t0, button1, t, inviteAccepted, round1, newRound, gameFinished, doubleClick, button2, button3, recieveGreenLight, recieveInviteTimedOut, button4], states=[
                         idle, connecting, waitingToAccept, playing, postGame], obj=player, name="player")
#hitw_functions = [attribute for attribute in dir(HoleInTheWall) if callable(getattr(HoleInTheWall, attribute)) if attribute.startswith("__") is False].replace('"', '')


driver = Driver()
driver.add_machine(player_machine)

myclient = MQTT_Client_1()
player.mqtt_client = myclient.client
myclient.stm_driver = driver

driver.start()
myclient.start(broker, port)
