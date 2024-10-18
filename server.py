import sys
import socket
import selectors
import logging
import json

#serverSelector = selectors.DefaultSelector()
selector = selectors.DefaultSelector()
logging.basicConfig(filename = 'server_connections.log', level = logging.INFO)
clients = {}


def start_game():
    
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind(('127.0.0.1', 65432)) #we may want to change this port ordering later
    lsock.listen(5) #we have 2 connections were listening for
    lsock.setblocking(False)
    selector.register(lsock, selectors.EVENT_READ, data=None)
    print("listening on 127.0.0.1:65432")

    while True:
        events = selector.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                service_connection(key, mask)

def accept_connection(sock):
    client_socket, addr = sock.accept()
    logging.info(f"connection created: {client_socket}")
    print("accepted a connection from client: ", addr)
    client_socket.setblocking(False)
    selector.register(client_socket, selectors.EVENT_READ, data=addr)
    clients[addr] = {"socket": client_socket, "state": "connected"}
    send_client_message(client_socket, addr, {"type": "welcome", "message": "Press button to start"})

def service_connection(key, mask):
    sock = key.fileobj
    addr = key.data
    try:
        data = sock.recv(1024)
        if data:
            handle_client_message(sock, addr, data)
        else:
            disconnect_client(sock, addr)
    except Exception as e:
        logging.error("Error in connection attempt: ", e)

def handle_client_message(sock, addr, data):
    try:
        message = json.loads(data.decode())
        logging.info(f"message received from {addr}: {message}")
        
        if message["type"] == "join":
            clients[addr]["state"] = "joined"
            broadcast_message({"type": "notice", "message": f"Player {addr} joined the game."})
        elif message["type"] == "move":
            # handle move command
            pass
        elif message["type"] == "chat":
            # handle chat message
            broadcast_message({"type": "chat", "message": message["message"]}, exclude=addr)
        elif message["type"] == "quit":
            disconnect_client(sock, addr)
    except Exception as e:
        logging.error("Error processing message: ", e)

def send_client_message(sock, addr, message):
    try:
        msg = json.dumps(message).encode()
        print(f"sending : {message} to {addr}")
        sock.send(msg)
    except Exception as e:
        logging.error("Error in message attempt: ", e)

def disconnect_client(sock, addr):
    print(f"disconnecting client: {addr}")
    if addr in clients:
        del clients[addr]
    selector.unregister(sock)
    sock.close()
    broadcast_message({"type": "notice", "message": f"Player {addr} left the game."})

def broadcast_message(message, exclude=None):
    msg = json.dumps(message).encode()
    for addr, client in clients.items():
        if addr != exclude:
            try:
                client["socket"].send(msg)
            except Exception as e:
                logging.error(f"Error sending broadcast message to {addr}: ", e)

start_game()
