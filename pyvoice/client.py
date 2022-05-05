#!/usr/bin/python3

import socket
import threading
import pyaudio
import stoppablethread as st

class Client:
    def __init__(self, target_ip, target_port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bool = True
        self.main_thread = threading.current_thread()
        
        while 1:
            try:
                self.target_ip = target_ip #input('Enter IP address of server --> ')
                self.target_port = target_port #int(input('Enter target port of server --> '))

                self.s.connect((self.target_ip, self.target_port))

                break
            except:
                print("Couldn't connect to server")

        chunk_size = 1024 # 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)
        
        print("Connected to Voice Server")

        # start threads
        global receive_thread
        receive_thread = st.StoppableThread(target=self.receive_server_data).start()
        self.send_data_to_server()

    def receive_server_data(self):
        while bool:
            try:
                if not self.main_thread.is_alive():
                    break
                data = self.s.recv(1024)
                self.playing_stream.write(data)
            except:
                pass


    def send_data_to_server(self):
        while bool:
            try:
                if not self.main_thread.is_alive():
                    break
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
            except:
                pass
    
    def terminate_client(self):
        try:
            print("client1")
            bool = False
            receive_thread.kill()
            receive_thread.join(0.0)
            print("client2")

            self.playing_stream.stop_stream()
            self.playing_stream.close()
            self.recording_stream.stop_stream()
            self.recording_stream.close()
            self.p.terminate()
            self.s.close()
            print("client3")
        except:
            pass


#client = Client()
