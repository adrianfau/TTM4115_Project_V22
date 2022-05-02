#!/usr/bin/python3

import socket
import threading
import stoppablethread as st

class Server:
    def __init__(self, port):
            self.ip = socket.gethostbyname(socket.gethostname())
            self.client_count = 0
            self.client_delta = 0
            #self.ip = "185.71.211.252"
            while 1:
                try:
                    self.port = port #int(input('Enter port number to run on --> '))

                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.bind((self.ip, self.port))

                    break
                except:
                    print("Couldn't bind to that port")

            self.connections = []
            self.accept_connections()

    def accept_connections(self):
        self.s.listen(100)

        print('Running on IP: '+self.ip+' | 185.71.211.252')
        print('Running on port: '+str(self.port))
        
        while True:
            c, addr = self.s.accept()

            self.connections.append(c)

            self.client_count = len(self.connections)
            if self.client_count != self.client_delta:
                print(f"{self.client_count} voice clients connected")
            self.client_delta = self.client_count

            global clienthandler_thread
            clienthandler_thread = st.StoppableThread(target=self.handle_client,args=(c,addr,)).start()
        
    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except:
                    pass

    def handle_client(self,c,addr):
        while 1:
            try:
                data = c.recv(1024)
                self.broadcast(c, data)
                if clienthandler_thread != None and clienthandler_thread.stopped():
                    return
            
            except socket.error:
                c.close()

    def terminate_server(self):
        try:
            clienthandler_thread.stop()
            clienthandler_thread.join()
            self.s.close()
        except:
            pass

#server = Server()
