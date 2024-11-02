import socket
import logging
import json
import threading

logging.basicConfig(filename='client_connections.log', level=logging.INFO)
player_id = None
codename = None
game_state = {}

def start_connection(host, port):
    addr = (host, port)

    try:
        print("Starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"Connection created: {addr}")
        sock.connect((host, port))

        threading.Thread(target=listen_to_server, args=(sock,)).start()

        while True:
            command = input("Enter command (codename/chat/join/move/quit): ")
            if command == "codename":
                codename_input = input("Enter your codename: ")
                send_client_message(sock, {"type": "codename", "codename": codename_input})
            elif command == "chat":
                chat_message = input("Enter your message: ")
                send_client_message(sock, {"type": "chat", "message": chat_message})
            elif command == "join":
                send_client_message(sock, {"type": "join"})
            elif command == "move":
                move_command = input("Enter your move: ")
                send_client_message(sock, {"type": "move", "move": move_command})
            elif command == "quit":
                send_client_message(sock, {"type": "quit"})
                break
            else:
                print("Unknown command. Try again.")

    except Exception as e:
        print("Error:", e)
        logging.error("Error in connection attempt:", e)

def listen_to_server(sock):
    global player_id, codename, game_state
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if data:
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    handle_server_message(json.loads(message))
            else:
                break
        except Exception as e:
            logging.error("Error receiving server message:", e)

def handle_server_message(message):
    global player_id, codename, game_state
    try:
        logging.info(f"Message received from server: {message}")

        if message["type"] == "welcome":
            player_id = message["player_id"]
            print(message["message"])
            print(f"Your Player ID: {player_id}")
        elif message["type"] == "chat":
            print(f"Chat message from {message['codename']}: {message['message']}")
        elif message["type"] == "notice":
            print(f"Notice: {message['message']}")
        elif message["type"] == "update":
            game_state = message["game_state"]
            current_turn = message["current_turn"]
            print(f"Game State: {game_state}")
            print(f"Current Turn: {current_turn}")
        elif message["type"] == "error":
            print(f"Error: {message['message']}")
    except Exception as e:
        logging.error("Error handling message:", e)

def send_client_message(sock, message):
    try:
        msg = json.dumps(message).encode() + b'\n'
        sock.send(msg)
        logging.info(f"Message sent to server: {message}")
    except Exception as e:
        logging.error("Error in message attempt:", e)

start_connection("127.0.0.1", 65432)
