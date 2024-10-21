
import socket
import logging
import json
import threading

logging.basicConfig(filename = 'client_connections.log', level = logging.INFO)
def start_connection(host, port):
    addr = (host, port)

    try:
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"connection created: {addr}")
        sock.connect((host,port))

        threading.Thread(target=listen_to_server, args=(sock,)).start()
    
        while True:
            command = input("Enter command (chat/join/move/quit): ")
            if command == "chat":
                chat_message = input("Enter your message: ")
                send_client_message(sock, {"type": "chat", "message": chat_message})
            elif command == "join":
                send_client_message(sock, {"type": "join", "message": "Player joined"})
            elif command == "move":
                move_command = input("Enter your move: ")
                send_client_message(sock, {"type": "move", "move": move_command})
            elif command == "quit":
                send_client_message(sock, {"type": "quit", "message": "Player leaving"})
                break
            else:
                print("Unknown command. Try again.")

    except Exception as e:
        print("Error: ", e)
        logging.error("Error in connection attempt: ", e)

def listen_to_server(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if message:
                handle_server_message(sock, json.loads(message))
            else:
                break
        except Exception as e:
            logging.error("Error receiving server message: ", e)

def handle_server_message(sock, message):
    try:
        logging.info(f"message received from server: {message}")
        if message["type"] == "welcome":
            print(message["message"])
        elif message["type"] == "chat":
            print(f"Chat message: {message['message']}")
        elif message["type"] == "notice":
            print(f"Notice: {message['message']}")
    except Exception as e:
        logging.error("Error processing server message: ", e)

def send_client_message(sock, message):
    try:
        msg = json.dumps(message).encode()
        sock.send(msg)
        logging.info(f"message sent to server: {message}")
    except Exception as e:
        logging.error("Error in message attempt: ", e)

start_connection("127.0.0.1", 65432)
