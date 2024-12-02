import logging
import json
from GUI import GUI
import tkinter as tk
import argparse

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
    parser = argparse.ArgumentParser(description="Process some flags.")
    parser.add_argument('-p', '--port', type=int, help='Specify the port number.')
    parser.add_argument('-i', '--ip', type=str, help='Specify the IP address.')

    args = parser.parse_args()
    main_window = tk.Tk()
    # Create an instance of the GUI class
    app = GUI(main_window)
    client = Client(app)
    print(args.ip, args.port)
    client.start_connection(args.ip, args.port)
