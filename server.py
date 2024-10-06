import sys
import socket
import selectors
import traceback
import threading
import logging
from threading import Semaphore

#serverSelector = selectors.DefaultSelector()
logging.basicConfig(filename = 'server_connections.log', level = logging.INFO)


def start_game():
    
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind(('127.0.0.1', 65432)) #we may want to change this port ordering later
    lsock.listen(5) #we have 2 connections were listening for

    print("listening on 127.0.0.1:65432")
    threads = []
    counter = 0
    maxClients = 2
    clients = []
    while len(clients) <= 2:
        try:
            clientSocket, addr = lsock.accept()
            clients.append(clientSocket)
            logging.info(f"connection created: {clientSocket}")
            print("accepted a connection from client: ", addr)
        
        # OPTIONAL, not sure if we need to multithread, but we can do it for now

            client_welcome_response(clientSocket, addr)
            if len(clients) == 2:
                clientSocket.send(b"Server is full, try again another time.")
                clientSocket.close()

        except Exception as e:
            logging.error("Error in connection attempt: ", e)

    for client in clients:
        message = client.recv(1024).decode()
        print(message)




        
def client_welcome_response(clientSocket, addr): #start of game introduction
        try:
            send_client_message(clientSocket, addr, b"Press button to start")
        except Exception as e:
            logging.error("Error in connection")

def send_client_message(clientSocket, addr, message):
    try:
        print(f"sending : {message} to {addr}")
        clientSocket.send(message)     
    except Exception as e:
         logging.error("Error in message attempt: ", e)
def client_start(clientSock, addr):
    message = clientSock.recv(1024).decode()
    logging.info(f"input recieved from user {message}")
    return message

start_game()
