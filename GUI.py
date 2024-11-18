import tkinter as tk
import socket
import logging
import json
import threading



class GUI:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.title("BattleShip")
        self.main_window.attributes("-fullscreen", True)

        # Get screen dimensions
        self.screen_width = self.main_window.winfo_screenwidth()
        self.screen_height = self.main_window.winfo_screenheight()

        # Initialize components
        self.start_button = None
        self.quit_button = None
        self.options_label = None
        self.menu = None
        self.confirmation_label = None
        self.player1_grid = None
        self.hits = {}
        self.opponent_board = {}
        self.frame = None
        self.chat_window = None
        self.chat_display = None
        self.entry_field = None
        self.messages = []
        self.name = None
        self.submit_ships_button = None
        self.host = None
        self.port = None
        self.sock = None
        self.server_conn_message = None
        self.thread = None
        
        # Ship size and max # of that ship type
        self.ships_info = {
            "Carrier": {"size": 5, "max": 1, "count": 0}, 
            "Battleship": {"size": 4, "max": 1, "count": 0}, 
            "Cruiser": {"size": 3, "max": 2, "count": 0}, 
            "Destroyer": {"size": 2, "max": 2, "count": 0}, 
            "Submarine": {"size": 1, "max": 2, "count": 0}
        }

        self.ship_to_place = None
        self.placed_cells = {}
        self.saved_board = set()
        self.ship_orientation = 'horizontal'
        
        self.canvas_width = 500
        self.canvas_height = 500
        self.canvas_x = (self.screen_width - self.canvas_width) // 2
        self.canvas_y = (self.screen_height - self.canvas_height) // 2

        # Ship selection buttons
        self.ship_buttons = []
        for i, (name, info) in enumerate(self.ships_info.items()):
            button = tk.Button(main_window, text=f"{name} ({info['size']})",
                command=lambda name=name: self.select_ship(name))
            button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + i * 30)
            self.ship_buttons.append(button)
        
        # Erase board button
        self.clear_button = tk.Button(main_window, text="Erase Board", command=self.clear_board)
        self.clear_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 6 * 30)

        # Ready up button
        self.ready_button = tk.Button(main_window, text="Ready Up", state=tk.DISABLED, command=self.on_ready_up)

        self.attack_button = tk.Button(main_window, text="Attack!", state=tk.DISABLED, command=self.attack)
        self.attack_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 8 * 30)

        self.hide_buttons()

        self.canvas = tk.Canvas(main_window, width=self.canvas_width, height=self.canvas_height) 
        self.canvas.place(x=self.canvas_x, y=self.canvas_y) # Center the grid based on screen size
        self.canvas.bind("<Motion>", self.highlight_cell)
        self.canvas.bind("<Button-1>", self.place_ship)

        self.turn = 1

        # Set up the main window UI components
        self.initialize_ui()
        self.main_window.bind("<Key>", self.rotate_ship)


    def initialize_ui(self):
    # Start Game button
        self.start_button = tk.Button(self.main_window, text="Start Game", font=("Helvetica", 24), width=10, height=2, relief="solid", padx=10, pady=5, command=self.open_name_window)
        self.start_button.place(relx=0.5, rely=0.5, anchor="center")

        # Quit button
        self.quit_button = tk.Button(self.main_window, text="Quit", font=("Helvetica", 24), width=10, height=2, relief="solid", padx=10, pady=5, command=self.main_window.quit)
        self.quit_button.place(relx=0.5, rely=0.6, anchor="center")

        # Options label
        self.options_label = tk.Label(self.main_window, text="Options", font=("Helvetica", 18), borderwidth=2, relief="solid", padx=10, pady=5)
        self.options_label.place(x=10, y=10)

        # Create menu for options
        self.menu = tk.Menu(self.main_window, tearoff=0)
        self.menu.add_command(label="Open Chat", command=self.open_chat_window)
        self.menu.add_command(label="Quit", command=self.main_window.quit)

        # Bind menu to options label click
        self.options_label.bind("<Button-1>", self.menu_show)

        # Current Turn label (initially hidden)
        self.current_turn_label = tk.Label(self.main_window, text="", font=("Helvetica", 18))



    def getSock(self):
        return self.sock

    def open_name_window(self):
        self.start_button.place_forget()
        self.quit_button.place_forget()

        self.server_conn_message = tk.Label(self.main_window, text=f"Connecting to server!", font=("Helvetica", 24))
        self.server_conn_message.place(relx=0.5, rely=0.5, anchor="center")

        addr = (self.host, self.port)
        print("Starting connection to", addr)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.info(f"Connection created: {addr}")
        self.sock.connect((self.host, self.port))
        self.thread = threading.Thread(target=self.listen_to_server).start()
        self.server_conn_message.place_forget()
        self.server_conn_message = tk.Label(self.main_window, text=f"Server Connected!", font=("Helvetica", 24))
        self.server_conn_message.place(relx=0.5, rely=0.5, anchor="center")
        self.main_window.after(5000, self.show_name_entry)
        #except Exception as e:
            #print("Error:", e)
            #logging.error("Error in connection attempt:", e)SS
            #self.server_conn_message.place_forget()
            #self.error_label = tk.Label(self.main_window, text=f"There was an error connecting to the server, check log for more information", font=("Helvetica", 24))
            #self.error_label.place(relx=0.5, rely=0.45, anchor="center")
        return True
    def show_name_entry(self):
        self.server_conn_message.place_forget()
        name_label = tk.Label(self.main_window, text="Enter your name:", font=("Helvetica", 24))
        name_label.place(relx=0.5, rely=0.45, anchor="center")

        name_entry = tk.Entry(self.main_window, font=("Helvetica", 24), justify="center")
        name_entry.place(relx=0.5, rely=0.5, anchor="center")

        def submit_name():
            self.name = name_entry.get()
            print(f"Name entered: {self.name}")
            name_label.place_forget()
            name_entry.place_forget()
            submit_button.place_forget()

                # Show confirmation label
            self.confirmation_label = tk.Label(self.main_window, text=f"Welcome, {self.name}!\nWaiting for other player to join...", font=("Helvetica", 24))
            self.confirmation_label.place(relx=0.5, rely=0.5, anchor="center")

            self.send_client_message({"type": "ready"})

                #opening game board after clients connect
        submit_button = tk.Button(self.main_window, text="Submit", font=("Helvetica", 14), command=submit_name)
        submit_button.place(relx=0.5, rely=0.55, anchor="center")

    def hide_confirmation_message(self):
        # Debug: Print when the message is being hidden
        print("Hiding confirmation message")

        # Hide the confirmation message after 5 seconds
        if self.confirmation_label:
            self.confirmation_label.place_forget()
        self.open_game_board()
        
    def send_client_message(self, message):
        try:
            msg = json.dumps(message).encode() + b'\n'
            self.sock.send(msg)
            logging.info(f"Message sent to server: {message}")
        except Exception as e:
            logging.error("Error in message attempt:", e)
    def menu_show(self, event):
        # Show the menu when the options label is clicked
        self.menu.post(event.x_root, event.y_root)

    def start_game(self, host, port):
        self.host = host
        self.port = port
        self.main_window.mainloop()

    def open_game_board(self):
        self.player_grids()
        self.main_window.update()
        self.show_buttons()

    def create_grid(self):
        self.cells = {}
        for row in range(10):
            for col in range(10):
                x1 = col * 50
                y1 = row * 50
                x2 = x1 + 50
                y2 = y1 + 50
                cell = self.canvas.create_rectangle(x1, y1, x2, y2, fill="light blue")
                self.cells[(row, col)] = cell

    def player_grids(self):
        print("showing grids")
        self.player1_grid = self.create_grid()
        # self.player2_grid = self.create_grid()


    def highlight_cell(self, event): 
        col = event.x // 50 
        row = event.y // 50

        for x in range(10):
            for y in range(10):
                if (x, y) not in self.placed_cells:
                    self.canvas.itemconfig(self.cells[(x, y)], fill="light blue")

        if 0 <= col < 10 and 0 <= row < 10 and self.ship_to_place:
            size  = self.ships_info[self.ship_to_place]["size"]
            if self.ship_orientation == 'horizontal':
                if col + size <= 10:
                    for i in range(size):
                        self.canvas.itemconfig(self.cells[(row, col + i)], fill="green")
            else:
                if row + size <= 10:
                    for i in range(size):
                        self.canvas.itemconfig(self.cells[(row + i, col)], fill="green") 

    
    def select_ship(self, name):
        if self.ships_info[name]["count"] < self.ships_info[name]["max"]:
            self.ship_to_place = name
    

    def place_ship(self, event):
        col = event.x // 50
        row = event.y // 50
        print(f"Placing {self.ship_to_place} at cell: ({row}, {col})")
        if self.ship_to_place:
            size = self.ships_info[self.ship_to_place]["size"]
            can_place = True

            if self.ship_orientation == "horizontal":
                if col + size <= 10:
                    for i in range(size):
                        if (row, col+i) in self.placed_cells:
                            can_place = False
                            break
                else:
                    can_place = False

                    # placed = True
            else:
                if row + size <= 10:
                    for i in range(size):
                        if (row + i, col) in self.placed_cells:
                            can_place = False
                            break
                else:
                    can_place = False
                        #placed = True
            
            if can_place:
                if self.ship_orientation == 'horizontal':
                    for i in range(size):
                        self.canvas.itemconfig(self.cells[(row, col + i)], fill="green")
                        self.placed_cells[(row, col + i)] = self.ship_to_place
                else:
                    for i in range(size):
                        self.canvas.itemconfig(self.cells[(row + i, col)], fill="green")
                        self.placed_cells[(row + i, col)] = self.ship_to_place

                self.ships_info[self.ship_to_place]["count"] += 1

                # Disable button when max # of ship type placed
                if self.ships_info[self.ship_to_place]["count"] == self.ships_info[self.ship_to_place]["max"]:
                    for button in self.ship_buttons: 
                        if button.cget("text").startswith(self.ship_to_place): 
                            button.config(state=tk.DISABLED) # Ship placed, reset the selection 
                # reset selection once ship is placed
                self.ship_to_place = None
        self.update_ready_state()
    
    def clear_board(self):
        # Reset board and ship counts
        for row in  range(10):
            for col in range(10):
                self.canvas.itemconfig(self.cells[(row, col)], fill="light blue")
        for name in self.ships_info:
            self.ships_info[name]["count"] = 0
        
        # Re-enable buttons
        for button in self.ship_buttons:
            button.config(state=tk.NORMAL)
        
        self.ships_to_place = None
        self.placed_cells.clear()
        print("Erased board")

    def rotate_ship(self, event):
        if event.keysym == 'r' or event.keysym == "R":
            self.ship_orientation = 'vertical' if self.ship_orientation == 'horizontal' else 'horizontal'
            print (f"Changing ship orientation to {self.ship_orientation}")

    def hide_buttons(self):
        for button in self.ship_buttons:
            button.place_forget()
        self.clear_button.place_forget()
        self.ready_button.place_forget()
        self.attack_button.place_forget()
        print("Hiding ship buttons")

    def show_buttons(self):
        for i, button in enumerate(self.ship_buttons):
            button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + i * 30)
        self.clear_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 6 * 30)
        self.ready_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 7 * 30)
        self.attack_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 8 * 30)
        print("Showing ship buttons")
    # Messaging Functionality

    def open_chat_window(self):
        self.chat_window = tk.Toplevel(self.main_window)
        self.chat_window.title("Chat Window")
        self.chat_window.geometry("400x300")

        self.chat_window.lift()  # Bring chat window to the front

        # Create a frame for holding the entry field and send button
        chat_frame = tk.Frame(self.chat_window)
        chat_frame.pack(side="bottom", fill="x", pady=10)

        self.chat_display = tk.Text(self.chat_window, width=40, height=10, wrap="word", state="disabled")
        self.chat_display.pack(pady=10, padx=10)

        # Entry field for typing a message
        self.entry_field = tk.Entry(chat_frame, width=40)
        self.entry_field.pack(side="top", pady=5, padx=10)

        # Send button below the entry field
        send_button = tk.Button(chat_frame, text="Send", command= self.send_message)
        send_button.pack(side="top", pady=5)

        self.simulate_server_messages()

        def minimize_chat_window():
            self.chat_window.withdraw()  # Hides the window instead of minimizing

    # You can add your own button if needed
        minimize_button = tk.Button(self.chat_window, text="Minimize", command=minimize_chat_window)
        minimize_button.pack(side="bottom", pady=10)
    def send_message(self):
        message = self.entry_field.get()
        if message:
            username = self.name
            self.messages.append({"user": username, "message": message})
            self.entry_field.delete(0, "end")
            self.update_chat()
    def update_chat(self):

        self.chat_display.config(state="normal")

        self.chat_display.delete(1.0, "end")

        for message in reversed(self.messages):
            self.chat_display.insert("1.0",f"{message['user']}: {message['message']}\n")
        #self.chat_display.yview("1.0")
        # Disable editing so the user can't modify the messages
        self.chat_display.yview("end")

        self.chat_display.config(state="disabled")
    def simulate_server_messages(self):
        # Simulate server sending messages every few seconds
        import random
        import time

        # This is a placeholder function to simulate receiving messages from the server
        def receive_message_from_server():
            # Simulate a new message from the server (could be replaced with actual server logic)
            new_message = f"Server message {random.randint(1, 100)}"
            username = "Server"  # Simulate server user
            self.messages.append({"user": username, "message": new_message})
            self.update_chat()

            # Call this function again after a short delay to simulate continuous updates
            self.chat_window.after(3000, receive_message_from_server)  # Update every 3 seconds

        receive_message_from_server()
    
    # Ready Up Functionality
    def check_ship_placed(self):
        for ship, details in self.ships_info():
            if details["count"] != details["max"]:
                return False
        return True
    
    def on_ready_up(self):
        # Save current board layout
        self.saved_board = self.placed_cells.copy()
        print("Board saved")
        self.clear_board()
        self.create_small_grid()
        self.canvas.bind("<Motion>", self.highlight_attack_cell)
        self.canvas.bind("<Button-1>", self.attack_cell)
        self.opponent_board_label = tk.Label(self.main_window, text="Opponent's Board", font=("Helvetica", 18)) 
        self.opponent_board_label.place(x=self.canvas_x + (self.canvas_width / 2), y=self.canvas_y - 30, anchor="center")
        
        print("board that is being sent", self.saved_board)
        json_compatible_dict = {str(key): value for key, value in self.saved_board.items()}
        print(json_compatible_dict)
        self.send_client_message({"type": "board", "message": json_compatible_dict})

        self.hide_buttons()
        self.attack_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 7 * 30)
        
    def highlight_attack_cell(self, event):
        col = event.x // 50
        row = event.y // 50

        for x in range(10):
            for y in range(10):
                coordinate = (x, y)
                if coordinate in self.hits:
                    if self.hits[coordinate] == 'Hit':
                        self.canvas.itemconfig(self.cells[(x, y)], fill="red")
                    elif self.hits[coordinate] == 'Miss':
                        self.canvas.itemconfig(self.cells[(x, y)], fill="yellow")
                else:
                    self.canvas.itemconfig(self.cells[(x, y)], fill="light blue")

        if 0 <= col < 10 and 0 <= row < 10:
            coordinate = (row, col)
            if coordinate not in self.hits and self.turn == 1:
                self.selected_cell = coordinate
                self.canvas.itemconfig(self.cells[coordinate], fill="red")
                self.attack_button.config(state=tk.NORMAL)
            else:
                self.attack_button.config(state=tk.DISABLED)



    
    def create_small_grid(self):
        small_canvas_width = 200
        small_canvas_height = 200
        small_canvas_x = self.canvas_x + self.canvas_width + 20
        small_canvas = tk.Canvas(self.main_window, width=small_canvas_width, height=small_canvas_height, bg="white")
        small_canvas.place(x=small_canvas_x, y=self.canvas_y)

        for row in range(10):
            for col in range(10):
                x1 = col * 20
                y1 = row * 20
                x2 = x1 + 20
                y2 = y1 + 20
                cell = small_canvas.create_rectangle(x1, y1, x2, y2, fill="light blue")
                if(row, col) in self.saved_board:
                    small_canvas.itemconfig(cell, fill="green")
        self.player_board_label = tk.Label(self.main_window, text="Your Board", font=("Helvetica", 18)) 
        self.player_board_label.place(x=small_canvas_x + (small_canvas_width / 2), y=self.canvas_y - 30, anchor="center")
    
    def update_ready_state(self):
        all_placed = all(info["count"] == info["max"] for info in self.ships_info.values()) 
        if all_placed: self.ready_button.config(state=tk.NORMAL) 
        else: self.ready_button.config(state=tk.DISABLED)
    
    def attack_cell(self, event):
        col = event.x // 50
        row = event.y // 50
        if self.selected_cell:
            for x in range(10):
                for y in range(10):
                    coordinate = (x, y)
                    if coordinate in self.hits:
                        if self.hits[coordinate] == 'Hit':
                            self.canvas.itemconfig(self.cells[(x, y)], fill="red")
                        elif self.hits[coordinate] == 'Miss':
                            self.canvas.itemconfig(self.cells[(x, y)], fill="yellow")
                    else:
                        self.canvas.itemconfig(self.cells[(x, y)], fill="light blue")

            # Highlight the newly selected cell
            if 0 <= col < 10 and 0 <= row < 10:
                coordinate = (row, col)
                if coordinate == self.selected_cell:
                    self.canvas.itemconfig(self.cells[coordinate], fill="red")

    
    def check_ship_sunk(self, row, col, board):
        ship_type = board[(row, col)]
        sunk = all(
            pos not in board or board [pos] != ship_type
            for pos in board
        )
        if sunk:
            print(f"{self.name}'s {ship_type} was sunk!")
    
    def attack(self):
        if self.selected_cell:
            row, col = self.selected_cell
            if (row, col) in self.opponent_board:
                self.canvas.itemconfig(self.cells[(row, col)], fill="red")
                self.hits[(row, col)] = 'Hit'
                print(f"{self.name}'s attack at ({row}, {col}) was a HIT!")
                self.check_ship_sunk(row, col, self.opponent_board)
            else:
                self.canvas.itemconfig(self.cells[(row, col)], fill="yellow")
                self.hits[(row, col)] = 'Miss'
                print(f"{self.name}'s attack at ({row}, {col}) was a MISS!")
            
            # Disable attack button, change turn, and update label
            self.attack_button.config(state=tk.DISABLED)
            self.turn = 2  # Change to opponent's turn
            self.current_turn_label.config(text=f"Player {self.turn}'s Turn")
            self.selected_cell = None  # Reset selected cell
            self.main_window.after(3000, self.update_attack_state)  # Simulate turn change delay
    
    def update_attack_state(self):
        if self.turn == 1:
            self.current_turn_label.config(text=f"Player {self.turn}'s Turn")
            self.canvas.bind("<Motion>", self.highlight_attack_cell)
            self.canvas.bind("<Button-1>", self.attack_cell)
        else:
            self.current_turn_label.config(text="")
            self.canvas.unbind("<Motion>")
            self.canvas.unbind("<Button-1>")




    def listen_to_server(self):
        print("Listening to server")
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
            if self.turn == 2:
                self.current_turn_label.config(text=f"Player {self.turn}'s Turn")
                self.turn = 1


    def handle_server_message(self, message):
        try:
            logging.info(f"Message received from server: {message}")

            if message["type"] == "notice":
                if message["message"] == "Please Create your board":
                    self.confirmation_label.place_forget()
                    self.show_buttons()
                    self.player_grids()
                    
            elif message["type"] == "chat":
                print(f"Chat message from {message['codename']}: {message['message']}")
            elif message["type"] == "opponent board":
                print("Opponent board received from server", message["message"])
                self.opponent_board = {eval(key): value for key, value in message["message"].items()}
            elif message["type"] == "turn":
                self.turn = message["message"]
                self.current_turn_label.config(text=f"Player {self.turn}'s Turn")
            else:
                print(f"Unknown message type: {message['type']}")
        except Exception as e:
            logging.error("Error handling message:", e)
    
    def check_win_condition(self):
        opponent_ships = set(self.opponent_board.values())
        if not opponent_ships:
            print(f"{self.name} wins!")
            self.current_turn_label.config(text=f"{self.name} wins!")
            self.end_game()
    
    def end_game(self):
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<Button-1>")
        self.attack_button.config(state=tk.DISABLED)
        self.ready_button.config(state=tk.DISABLED)



        
# Create the main application window
# Create an instance of the GUI class
