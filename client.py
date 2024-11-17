import socket
import logging
import json
import threading
from GUI import GUI
import tkinter as tk

class Client:
    def __init__(self, gui):
        self.GUI = gui
        self.player_id = None
        self.codename = None
        self.game_state = {}
        self.in_game = False
        self.available_commands = []
        self.server_thread = None
        logging.basicConfig(filename='client_connections.log', level=logging.INFO)


    def start_connection(self, host, port):
    
        self.GUI.start_game(host, port)
        self.server_thread = threading.Thread(target=self.listen_to_server).start()




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

            
            if message["type"] == "chat":
                print(f"Chat message from {message['codename']}: {message['message']}")
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
    main_window = tk.Tk()

    # Create an instance of the GUI class
    app = GUI(main_window)
    main_window.bind("<Key>", app.rotate_ship)

    #app.start_game()
    client = Client(app)
    client.start_connection("127.0.0.1", 65432)
