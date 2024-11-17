import tkinter as tk


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
        self.player2_grid = None
        self.frame = None
        self.chat_window = None
        self.chat_display = None
        self.entry_field = None
        self.messages = []
        self.name = None
        
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

        self.hide_buttons()

        self.canvas = tk.Canvas(main_window, width=self.canvas_width, height=self.canvas_height) 
        self.canvas.place(x=self.canvas_x, y=self.canvas_y) # Center the grid based on screen size
        self.canvas.bind("<Motion>", self.highlight_cell)
        self.canvas.bind("<Button-1>", self.place_ship)

        self.turn = 1

        # Set up the main window UI components
        self.initialize_ui()

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

    def option_selected(self, option):
        print(f"{option} selected!")

    def open_name_window(self):
        self.start_button.place_forget()
        self.quit_button.place_forget()

        # Create name entry label and entry box
        name_label = tk.Label(self.main_window, text="Enter your name:", font=("Helvetica", 24))
        name_label.place(relx=0.5, rely=0.45, anchor="center")

        name_entry = tk.Entry(self.main_window, font=("Helvetica", 24), justify="center")
        name_entry.place(relx=0.5, rely=0.5, anchor="center")

        def submit_name():
            self.name = name_entry.get()
            print(f"Name entered: {self.name}")
            # Hide name entry components
            name_label.place_forget()
            name_entry.place_forget()
            submit_button.place_forget()

            # Show confirmation label
            self.confirmation_label = tk.Label(self.main_window, text=f"Welcome, {self.name}!\nWaiting for other player to join...", font=("Helvetica", 24))
            self.confirmation_label.place(relx=0.5, rely=0.5, anchor="center")
            self.main_window.after(5000, self.hide_confirmation_message)
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

    def menu_show(self, event):
        # Show the menu when the options label is clicked
        self.menu.post(event.x_root, event.y_root)

    def start_game(self):
        main_window.mainloop()

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
        self.player2_grid = self.create_grid()


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
        self.update_button_state()
    
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
        print("Hiding ship buttons")

    def show_buttons(self):
        for i, button in enumerate(self.ship_buttons):
            button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + i * 30)
        self.clear_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 6 * 30)
        self.ready_button.place(x=self.canvas_x + self.canvas_width + 20, y=self.canvas_y + 7 * 30)
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
        # Update ready button to attack button
        self.ready_button.config(text="Attack")
        self.ready_button.config(command=self.attack)
        self.canvas.bind("<Motion>", self.highlight_attack_cell)
        self.canvas.bind("<Button-1>", self.attack_cell)
    
    def highlight_attack_cell(self, event): 
        col = event.x // 50 
        row = event.y // 50 
        
        for (x, y), cell in self.cells.items(): 
            if (x, y) in self.saved_board: self.canvas.itemconfig(cell, fill="green") 
            elif self.canvas.itemcget(cell, 'fill') == 'yellow': self.canvas.itemconfig(cell, fill="yellow") 
            elif self.canvas.itemcget(cell, 'fill') == 'red': self.canvas.itemconfig(cell, fill="red") 
            else: self.canvas.itemconfig(cell, fill="light blue")

            if 0 <= col < 10 and 0 <= row < 10: self.canvas.itemconfig(self.cells[(row, col)], fill="red")

    
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
    
    def update_button_state(self):
        all_placed = all(info["count"] == info["max"] for info in self.ships_info.values()) 
        if all_placed: self.ready_button.config(state=tk.NORMAL) 
        else: self.ready_button.config(state=tk.DISABLED)
    
    def attack_cell(self, event):
        col = event.x // 50
        row = event.y // 50
        print(f"{self.name} fired a shot at ({row}, {col})")

        if self.turn == 1:
            if (row, col) in self.saved_board:
                self.canvas.itemconfig(self.cells[(row, col)], fill="red")
                print(f"{self.name}'s {self.saved_board[(row, col)]} was HIT!")
                self.check_ship_sunk(row, col, self.saved_board)
            else:
                self.canvas.itemconfig(self.cells[(row, col)], fill="yellow")
                print("MISS!")
            
            self.turn = 2
        
        elif self.turn == 2:
            if (row, col) in self.saved_board:
                self.canvas.itemconfig(self.cells[(row, col)], fill="red")
                print(f"{self.name}'s {self.saved_board[(row, col)]} was HIT!")
                self.check_ship_sunk(row, col, self.saved_board)
            else:
                self.canvas.itemconfig(self.cells[(row, col)], fill="yellow")
                print("MISS!")
            
            self.turn = 1
    
    def check_ship_sunk(self, row, col, board):
        ship_type = board[(row, col)]
        sunk = all(
            pos not in board or board [pos] != ship_type
            for pos in board
        )
        if sunk:
            print(f"{self.name}'s {ship_type} was sunk!")
    
    def attack(self):
        if (self.turn == 1):
            print(f"{self.name} is attacking")
        else:
            print("It is not your turn!")
        


# Create the main application window
main_window = tk.Tk()

# Create an instance of the GUI class
app = GUI(main_window)
main_window.bind("<Key>", app.rotate_ship)

app.start_game()
