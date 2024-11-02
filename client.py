import socket
import logging
import json
import threading

class Client:
    def __init__(self):
        self.player_id = None
        self.codename = None
        self.game_state = {}
        self.in_game = False
        self.available_commands = []
        logging.basicConfig(filename='client_connections.log', level=logging.INFO)


    def start_connection(self, host, port):
        addr = (host, port)
        try:
            print("Starting connection to", addr)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logging.info(f"Connection created: {addr}")
            self.sock.connect((host, port))
            self.available_commands = ["codename", "chat", "ready", "quit"]
            

            threading.Thread(target=self.listen_to_server).start()

            while True:
                command = self.get_command()
                if command == "codename":
                    codename_input = input("Enter your codename: ")
                    self.send_client_message({"type": "codename", "codename": codename_input})
                elif command == "chat":
                    chat_message = input("Enter your message: ")
                    self.send_client_message({"type": "chat", "message": chat_message})
                elif command == "ready":
                    self.send_client_message({"type": "ready"})
                elif command == "check_board":
                    self.send_client_message({"type": "check_board"})
                elif command == "move":
                    move_command = input("Enter shot coordinate (e.g., B7): ")
                    self.send_client_message({"type": "move", "move": move_command})
                elif command == "quit":
                    self.send_client_message({"type": "quit"})
                    break
                else:
                    print("Unknown command. Try again.")

        except Exception as e:
            print("Error:", e)
            logging.error("Error in connection attempt:", e)

    def get_command(self):
        return input(f"Enter command ({'/'.join(self.available_commands)}): ")
    

    def listen_to_server(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(1024).decode()
                if data:
                    buffer += data
                    while '\n' in buffer:
                        message, buffer = buffer.split('\n', 1)
                        self.handle_server_message(json.loads(message))
                else:
                    break
            except Exception as e:
                logging.error("Error receiving server message:", e)

    def handle_server_message(self, message):
        try:
            logging.info(f"Message received from server: {message}")

            if message["type"] == "welcome":
                self.player_id = message["player_id"]
                print(message["message"])
                print(f"Your Player ID: {self.player_id}")
            elif message["type"] == "chat":
                print(f"Chat message from {message['codename']}: {message['message']}")
            elif message["type"] == "notice":
                print(f"Notice: {message['message']}")
            elif message["type"] == "update":
                self.game_state = message["game_state"]
                current_turn = message["current_turn"]
                self.in_game = True
                print(f"Current Turn: {current_turn}")
            elif message["type"] == "board_status": # When GUI is made, this will be removed
                print(f"Your moves: {message['moves']}")
                print(f"Ships you've sunk: {message['sank_ships']}")
                print(f"Game State: {message['game_state']}")
            elif message["type"] == "error":
                print(f"Error: {message['message']}")
            elif message["type"] == "move_result":
                print(f"Move result: {message['result']}")
            elif message["type"] == "update_commands":
                self.available_commands = message["commands"]
            else:
                print(f"Unknown message type: {message['type']}")
        except Exception as e:
            logging.error("Error handling message:", e)




    def send_client_message(self, message):
        try:
            msg = json.dumps(message).encode() + b'\n'
            self.sock.send(msg)
            logging.info(f"Message sent to server: {message}")
        except Exception as e:
            logging.error("Error in message attempt:", e)

if __name__ == "__main__":
    client = Client()
    client.start_connection("127.0.0.1", 65432)
