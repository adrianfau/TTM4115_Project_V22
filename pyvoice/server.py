#!/usr/bin/python3

import socket
import threading
import stopthread as st

class Server:
    def __init__(self, port):
            self.ip = socket.gethostbyname(socket.gethostname())
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

        print('Running on IP: '+self.ip)
        print('Running on port: '+str(self.port))
        
        while True:
            c, addr = self.s.accept()

            self.connections.append(c)

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
                if clienthandler_thread.stopped():
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
