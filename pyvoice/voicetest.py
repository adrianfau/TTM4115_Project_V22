import client, server
import stoppablethread as st
import socket

print(socket.gethostbyname(socket.gethostname()))
voiceip = socket.gethostbyname(socket.gethostname())
voiceport = 55099
def createVoiceServer(port):
    voice_server = server.Server(port)
def createVoiceClient(voiceip, voiceport):
    voice_client = client.Client(voiceip, voiceport)

def run_server_and_client():
    print("running server and voice client")
    voiceserver_thread = st.StoppableThread(target = createVoiceServer, args=(voiceport,)).start()
    voiceclient_thread = st.StoppableThread(target = createVoiceClient, args=(voiceip, voiceport,)).start()

def run_only_client():
    print("running voiceclient")
    voiceclient_thread2 = st.StoppableThread(target = createVoiceClient, args=("192.168.56.1", voiceport)).start()

run_server_and_client()
#run_only_client()