import sys
import socket
import selectors
import traceback
import threading

serverSelector = selectors.DefaultSelector()



def start():
    
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind(('127.0.0.1', 65432)) #we may want to change this port ordering later
    lsock.listen(2) #we have 2 connections were listening for

    print("listening on 127.0.0.1:65432")

    clients = 0 # need to keep track of total clients
    while clients < 2:
        clientSocket, addr = lsock.accept()
        print("accepted a connection from client: ", addr)
        clients += 1

        # OPTIONAL, not sure if we need to multithread, but we can do it for now

        client_thread = threading.Thread(target=client_response, args=(clientSocket,addr))
        client_thread.start()

def client_response(clientSocket, addr):
    while True:
        message = clientSocket.recv(1024) # need to adjust size based on implementation
        print("Recieved a message from ", addr)
        print("message recieved: ", message.decode())

start()
