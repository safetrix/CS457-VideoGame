import sys
import socket
import selectors
import logging
import json
import uuid

selector = selectors.DefaultSelector()
logging.basicConfig(filename='server_connections.log', level=logging.INFO)
clients = {}
game_state = {}
turn_order = []
current_turn = 0

def start_game():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind(('127.0.0.1', 65432))
    lsock.listen(5)
    lsock.setblocking(False)
    selector.register(lsock, selectors.EVENT_READ, data=None)
    print("Listening on 127.0.0.1:65432")

    while True:
        events = selector.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                service_connection(key, mask)

def accept_connection(sock):
    client_socket, addr = sock.accept()
    logging.info(f"Connection created: {client_socket}")
    print(f"Accepted a connection from client: {addr}")
    client_socket.setblocking(False)
    player_id = str(uuid.uuid4())
    selector.register(client_socket, selectors.EVENT_READ, data=player_id)
    clients[player_id] = {"socket": client_socket, "state": "connected", "addr": addr, "codename": None}
    send_client_message(client_socket, {"type": "welcome", "message": "Enter your codename:", "player_id": player_id})

def service_connection(key, mask):
    sock = key.fileobj
    player_id = key.data
    try:
        data = sock.recv(1024)
        if data:
            handle_client_message(sock, player_id, data)
        else:
            disconnect_client(sock, player_id)
    except Exception as e:
        logging.error(f"Error in connection attempt: {e}")

def handle_client_message(sock, player_id, data):
    try:
        message = json.loads(data.decode())
        logging.info(f"Message received from {player_id}: {message}")

        if message["type"] == "codename":
            clients[player_id]["codename"] = message["codename"]
            send_client_message(sock, {"type": "notice", "message": f"Your codename is set to {message['codename']}"})
            broadcast_message({"type": "notice", "message": f"Player {message['codename']} joined the game."})
            update_game_state()
        elif message["type"] == "join":
            clients[player_id]["state"] = "joined"
            if player_id not in turn_order:
                turn_order.append(player_id)
            broadcast_message({"type": "notice", "message": f"Player {clients[player_id]['codename']} joined the game."})
            update_game_state()
        elif message["type"] == "move":
            if turn_order[current_turn] == player_id:
                game_state[player_id] = message["move"]
                current_turn = (current_turn + 1) % len(turn_order)
                update_game_state()
            else:
                send_client_message(sock, {"type": "error", "message": "It's not your turn!"})
        elif message["type"] == "chat":
            broadcast_message({"type": "chat", "message": message["message"], "codename": clients[player_id]["codename"]})
        elif message["type"] == "quit":
            disconnect_client(sock, player_id)
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def send_client_message(sock, message):
    try:
        msg = json.dumps(message).encode() + b'\n'
        sock.send(msg)
        logging.info(f"Message sent to client: {message}")
    except Exception as e:
        logging.error(f"Error in message attempt: {e}")

def disconnect_client(sock, player_id):
    print(f"Disconnecting client: {player_id}")
    if player_id in clients:
        del clients[player_id]
    if player_id in turn_order:
        turn_order.remove(player_id)
    selector.unregister(sock)
    sock.close()
    broadcast_message({"type": "notice", "message": f"Player {player_id} left the game."})
    update_game_state()

def broadcast_message(message, exclude=None):
    msg = json.dumps(message).encode() + b'\n'
    for client_id, client in clients.items():
        if client_id != exclude:
            try:
                client["socket"].send(msg)
            except Exception as e:
                logging.error(f"Error sending broadcast message to {client_id}: {e}")

def update_game_state():
    broadcast_message({"type": "update", "game_state": game_state, "current_turn": turn_order[current_turn] if turn_order else None})

start_game()
