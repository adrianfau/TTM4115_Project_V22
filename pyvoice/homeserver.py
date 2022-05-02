import server
import socket

print("----Starting Voice Server----")
voiceip = socket.gethostbyname(socket.gethostname())
voiceport = 10505
voice_server = server.Server(voiceport)