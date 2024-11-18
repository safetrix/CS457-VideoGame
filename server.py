import socket
import selectors
import logging
import json
import uuid

class Server:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.clients = {}
        self.turn_order = []
        self.current_turn = 0
        self.ready_players = set()
        self.board1 = []
        self.board2 = []
        logging.basicConfig(filename='server_connections.log', level=logging.DEBUG)  # Set to DEBUG level

    def start_game(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind(('127.0.0.1', 65432))
        lsock.listen(5)
        lsock.setblocking(False)
        self.selector.register(lsock, selectors.EVENT_READ, data=None)
        print("Listening on 127.0.0.1:65432")

        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_connection(key.fileobj)
                else:
                    self.service_connection(key, mask)

    def accept_connection(self, sock):
        client_socket, addr = sock.accept()
        logging.info(f"Connection created: {client_socket}")
        print(f"Accepted a connection from client: {addr}")
        client_socket.setblocking(False)
        player_id = str(uuid.uuid4())
        self.selector.register(client_socket, selectors.EVENT_READ, data=player_id)
        self.clients[player_id] = {"socket": client_socket, "state": "connected", "addr": addr, "codename": None, "ready": False, "board": self.default_board(), "moves": [], "sank_ships": []}

    def service_connection(self, key, mask):
        sock = key.fileobj
        player_id = key.data
        try:
            data = sock.recv(1024)
            if data:
                self.handle_client_message(sock, player_id, data)
            else:
                self.disconnect_client(sock, player_id)
        except Exception as e:
            logging.error(f"Error in connection attempt: {e}")

    def handle_client_message(self, sock, player_id, data):
        try:
            message = json.loads(data.decode())
            logging.info(f"Message received from {player_id}: {message}")
            print(f"Message from {player_id}: {message}")
            if message["type"] == "ready":
                self.clients[player_id]["ready"] = True
                self.ready_players.add(player_id)
                logging.debug(f"Player is ready. Ready players: {len(self.ready_players)}")
                print((f"Player is ready. Ready players: {len(self.ready_players)}"))
                if len(self.ready_players) == 2:
                    self.start_battleship() #send messgae to players saying both connected
            elif message["type"] =="board":
                print("board sent from client ", message["message"])
                print("Sending opponent board to the client")
                self.send_client_message(self.clients[next(pid for pid in self.clients if pid != player_id)]["socket"], {"type": "opponent board", "message": message["message"]})
                 #this ensures the board is sent to the other PID
                

            elif message["type"] == "move":
                pass
            elif message["type"] == "chat":
                self.broadcast_message({"type": "chat", "message": message["message"], "codename": self.clients[player_id]["codename"]})
            elif message["type"] == "check_board":
                self.send_client_message(sock, {
                    "type": "board_status", 
                    "game_state": self.get_game_state(),  # Include game state
                    "moves": self.clients[player_id]["moves"], 
                    "sank_ships": self.clients[player_id]["sank_ships"]
                })
            elif message["type"] == "quit":
                self.disconnect_client(sock, player_id)
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    def check_win_condition(self, opponent_id):
        # Implement win condition check here once GUI is implemented
        return False

    def reset_game(self):
        self.ready_players.clear()
        for client_id in self.clients:
            self.clients[client_id]["ready"] = False
            self.clients[client_id]["in_game"] = False
            self.clients[client_id]["board"] = self.default_board()
            self.clients[client_id]["moves"] = []
            self.clients[client_id]["sank_ships"] = []
        self.broadcast_message({"type": "notice", "message": "The game has ended. Returning to the pregame lobby."})
        self.broadcast_message({"type": "update_commands", "commands": ["codename", "chat", "ready", "quit"]})


    def send_client_message(self, sock, message):
        try:
            msg = json.dumps(message).encode() + b'\n'
            sock.send(msg)
            logging.info(f"Message sent to client: {message}")
        except Exception as e:
            logging.error(f"Error in message attempt: {e}")

    def disconnect_client(self, sock, player_id):
        print(f"Disconnecting client: {player_id}")
        if player_id in self.clients:
            del self.clients[player_id]
        if player_id in self.turn_order:
            self.turn_order.remove(player_id)
        self.selector.unregister(sock)
        sock.close()
        self.broadcast_message({"type": "notice", "message": f"Player {self.clients[player_id]['codename']} left the game."})

    def broadcast_message(self, message, exclude=None):
        msg = json.dumps(message).encode() + b'\n'
        for client_id, client in self.clients.items():
            if client_id != exclude:
                try:
                    client["socket"].send(msg)
                except Exception as e:
                    logging.error(f"Error sending broadcast message to {client_id}: {e}")
    
    def notify_game_start(self):
        for client_id in self.clients:
            self.clients[client_id]["in_game"] = True
            self.send_client_message(self.clients[client_id]["socket"], {
                "type": "notice",
                "message": "The game has started! Available commands: chat/check_board/move/quit"
            })
            self.send_client_message(self.clients[client_id]["socket"], {
                "type": "update_commands",
                "commands": ["chat", "check_board", "move", "quit"]
            })

    def start_battleship(self):
        logging.debug("Both players are ready. Starting game...")
        self.broadcast_message({"type": "notice", "message": f"Please Create your board"})
        print("sending message to players")

    def default_board(self): # Empty board for now, custom boards will be used in GUI
        return {f"{chr(65 + row)}{col + 1}": "empty" for row in range(10) for col in range(10)}

    def valid_move(self, move, opponent_id):
        return move in self.clients[opponent_id]["board"]

    def get_game_state(self):
        return {pid: {"board": self.clients[pid]["board"], "moves": self.clients[pid]["moves"], "sank_ships": self.clients[pid]["sank_ships"]} for pid in self.turn_order}

if __name__ == "__main__":
    server = Server()
    server.start_game()
