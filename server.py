import socket
import selectors
import logging
import json
import uuid
import random
import argparse

class Server:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.clients = {}
        self.ready_players = set()
        self.board1 = []
        self.board2 = []
        self.board_count = None

        self.player_order = []
        self.current_turn_index = 0

        logging.basicConfig(filename='server_connections.log', level=logging.DEBUG)  # Set to DEBUG level

    def start_game(self, port):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind(('0.0.0.0', port))
        print(lsock.getsockname())
        lsock.listen(5)
        lsock.setblocking(False)
        self.selector.register(lsock, selectors.EVENT_READ, data=None)
        print(f"Listening on 0.0.0.0:{port}")

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
        self.player_order.append(player_id)

        self.send_client_message(client_socket, {"type": "player_id", "message": player_id})

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
                self.ready_players  -= 1
            elif message["type"] == "update_turn":
                if(self.current_turn_index + 1) < len(self.player_order):
                    self.current_turn_index = self.current_turn_index + 1
                else:
                    self.current_turn_index = 0
                for client_id in self.clients:
                    self.send_client_message(self.clients[client_id]["socket"], {
                "type": "turn",
                "message": self.current_turn_index
            })
            elif message["type"] == "game over":
                self.broadcast_message({"type": "game over"})
            elif message["type"] == "ship_sunk":
                self.broadcast_message({"type": "ship_sunk"})
                print("Notifying opponent of sunk ship.")
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
        if player_id in self.player_order:
            self.player_order.remove(player_id)
        self.selector.unregister(sock)
        sock.close()
        self.broadcast_message({"type": "notice", "message": f"Player {self.clients[player_id]['codename']} left the game."})
        self.player_order.remove(player_id)

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

        if len(self.player_order) == 2:
            random.shuffle(self.player_order)
            self.current_turn_index = 0
            current_player = self.player_order[self.current_turn_index]
            print(f"Game has started. {current_player} goes first.")

            for client_id in self.clients:
                    self.send_client_message(self.clients[client_id]["socket"], {
                "type": "player_order",
                "message": self.player_order
            })
            
        
        # self.turn_order = list(self.ready_players)  # Ensure turn order matches the players
        # random.shuffle(self.turn_order)  # Shuffle to select who starts first
        # self.current_turn = 0
        # self.notify_game_start()  # Notify both clients that the game has started
        # current_player = self.clients[self.turn_order[self.current_turn]]["codename"]  # Define current_player
        # self.broadcast_message({
        #     "type": "notice",
        #     "message": f"The game has started! {current_player} goes first."
        # })
        # self.broadcast_message({
        #     "type": "update",
        #     "game_state": self.get_game_state(),
        #     "current_turn": current_player  # Send codename instead of player ID
        # })


    def default_board(self): # Empty board for now, custom boards will be used in GUI
        return {f"{chr(65 + row)}{col + 1}": "empty" for row in range(10) for col in range(10)}

    def valid_move(self, move, opponent_id):
        return move in self.clients[opponent_id]["board"]

    def get_game_state(self):
        return {pid: {"board": self.clients[pid]["board"], "moves": self.clients[pid]["moves"], "sank_ships": self.clients[pid]["sank_ships"]} for pid in self.player_order}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some flags.")
    parser.add_argument('-p', '--port', type=int, help='Specify the port number.')
    args = parser.parse_args()

    print("Port that is selected for server", args.port)

    server = Server()
    server.start_game(args.port)
