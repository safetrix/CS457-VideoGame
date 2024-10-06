import sys
import socket
import selectors
import traceback
import threading
import logging

#serverSelector = selectors.DefaultSelector()
logging.basicConfig(filename = 'connections.log', level = logging.INFO)


def start():
    
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind(('127.0.0.1', 65432)) #we may want to change this port ordering later
    lsock.listen(2) #we have 2 connections were listening for

    print("listening on 127.0.0.1:65432")

 
    clients = 0 # need to keep track of total clients
    while clients < 2:
        try:
            clientSocket, addr = lsock.accept()
            logging.info(f"connection created: {clientSocket}")
            print("accepted a connection from client: ", addr)
            clients += 1
        
        # OPTIONAL, not sure if we need to multithread, but we can do it for now

            client_thread = threading.Thread(target=client_response, args=(clientSocket,addr))
            client_thread.start()
        except Exception as e:
            logging.error("Error in connection attempt: ", e)

def client_response(clientSocket, addr):
    while True:
        message = clientSocket.recv(1024) # need to adjust size based on implementation

        if not message:
            break
        print("Recieved a message from ", addr)
        print("message recieved: ", message.decode())
        print("sending messages back to client")
        clientSocket.send(b"ACK")
        

start()
