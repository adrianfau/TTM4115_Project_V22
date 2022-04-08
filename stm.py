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
        self.button = gz.Button(1)
        self.led = gz.LED(1)
        self.greenLightOn = self.led.on
        self.greenLightOff = self.led.off
        self.own_score = 0
        self.round_number = 0

    def on_button_press(self, b):
        self.stm.send('button1')

    def terminateSession():
        print("a")

    def startGameSession():
        print("b")

    def startGame():
        print("c")
        movenet_detector = mv.MoveNet()

    def showScores():
        print("d")

    def waitingToAccept():
        print("e")

    def greenLight():
        self.led.on

    def lightOff():
        self.led.off

    def sendGreenLight():
        myclient.publish(user2_topic, "greenlight")

    def sendGameInvite():
        myclient.publish(user2_topic, "gameinvite")

    def sendInviteTimedOut:
        myclient.publish(user2_topic, "")

    def receiveInviteTimedOut:
        self.led.on

    def receiveGreenLight():
        print("asd")

    def endGame():
        print("asd")


t0 = {'source': 'initial',
      'target': 'idle'}

# Change 1: effect is removed
t1 = {'trigger': 'button1',
      'source': 'idle',
      'target': 'connecting'}

# Change 2: effect is removed here, too
t2 = {'trigger': 't',
      'source': 'connecting',
      'target': 'idle'}

t2 = {'trigger': 't',
      'source': 'connecting',
      'target': 'idle'}

t3 = {'trigger': 'inviteAccepted',
      'source': 'connecting',
      'target': 'playing'}

t4 = {'trigger': 'gameFinished',
      'source': 'playing',
      'target': 'postgame'}

t5 = {'trigger': 'button1',
      'source': 'playing',
      'target': 'idle'}

t6 = {'trigger': 'receiveGreenLight',
      'source': 'idle',
      'target': 'waitingToAccept'}

t7 = {'trigger': 'receiveInviteTimedOut',
      'source': 'waitingToAccept',
      'target': 'idle'}

t8 = {'trigger': 'button1',
      'source': 'waitingToAccept',
      'target': 'playing'}

t9 = {'trigger': 'button1',
      'source': 'postgame',
      'target': 'idle'}

t10 = {'trigger': 'doubleclick',
       'source': 'postgame',
       'target': 'playing'}

# Change 3: We declare dicts for the states
idle = {'name': 'idle',
        'entry': 'terminateGameSession; start_timer("t", 6000)'
        }

connecting = {'name': 'connecting',
              'entry': 'sendGameInvite; start_timer("t", 1000)'
              }

waitingToAccept = {'name': 'waitingToAccept',
                   'entry': 'greenLight; start_timer("t", 1000)'
                   }

playing = {'name': 'playing',
           'entry': 'startGame; start_timer("t", 1000)'
           }

postgame = {'name': 'postgame',
            'entry': 'showScores; start_timer("t", 1000)'
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
player_machine = Machine(transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10], states=[
                         idle, connecting, waitingToAccept, playing, postgame], obj=player, name="player")
hitw_functions = [attribute for attribute in dir(HoleInTheWall) if callable(getattr(HoleInTheWall, attribute)) if attribute.startswith("__") is false].replace('"', '')

driver = Driver()
driver.add_machine(player_machine)

myclient = MQTT_Client_1()
player.mqtt_client = myclient.client
myclient.stm_driver = driver

driver.start()
myclient.start(broker, port)
