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
       


    def get_command(self):
        return input(f"Enter command ({'/'.join(self.available_commands)}): ")
    

  

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
    client = Client(app)
    client.start_connection("127.0.0.1", 65432)
