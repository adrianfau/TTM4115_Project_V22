from stmpy import Driver, Machine
import paho.mqtt.client as mqtt
import gpiozero as gz

print("Hello, World!")

class HoleInTheWall:
    def __init__(self):
        self.button = gz.Button(1)
        self.led = gz.LED(1)
        self.greenLightOn = self.led.on
        self.greenLightOff = self.led.off

    def on_button_press(self, b):
        self.stm.send('button1')
    

    def terminateSession():
        print("a")
    def startGameSession():
        print("b")
    def startGame():
        print("c")
    def showScores():
        print("d")
    def waitingToAccept():
        print("e")
    def greenLight():
    def sendGreenLight():
        print("asd")
    def sendGameInvite():
        print("asd")
    def sendInviteTimedOut:
        print("asd")
    def receiveInviteTimedOut:
        print("asd")
    def receiveGreenLight():
        print("asd")
    def endGame():
        print("asd")

t0 = {'source': 'initial',
      'target': 'idle'}

# Change 1: effect is removed
t1 = {'trigger':'button1',
      'source':'idle',
      'target':'connecting'}

# Change 2: effect is removed here, too
t2 = {'trigger':'t', 
      'source':'connecting', 
      'target':'idle'}

t2 = {'trigger':'t', 
      'source':'connecting', 
      'target':'idle'}

t3 = {'trigger':'inviteAccepted', 
      'source':'connecting', 
      'target':'playing'}

t4 = {'trigger':'gameFinished', 
      'source':'playing', 
      'target':'postgame'}

t5 = {'trigger':'button1', 
      'source':'playing', 
      'target':'idle'}

t6 = {'trigger':'receiveGreenLight', 
      'source':'idle', 
      'target':'waitingToAccept'}

t7 = {'trigger':'receiveInviteTimedOut', 
      'source':'waitingToAccept', 
      'target':'idle'}

t8 = {'trigger':'button1', 
      'source':'waitingToAccept', 
      'target':'playing'}

t9 = {'trigger':'button1', 
      'source':'postgame', 
      'target':'idle'}

t10 = {'trigger':'doubleclick', 
      'source':'postgame', 
      'target':'playing'}

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
