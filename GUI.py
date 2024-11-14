import tkinter as tk


class GUI:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.title("BattleShip")
        self.main_window.attributes("-fullscreen", True)

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
    def create_grid(self, x_position, title):
        print("creating grid now")
        frame = tk.Frame(self.main_window)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title_label = tk.Label(self.frame, text="Create your board", font=("Arial", 24, "bold"))
        title_label.pack(side="top", pady=10)
        for row in range(10):
            for col in range(10):
                button = tk.Button(frame, text=" ", width=4, height=2,
                           command=lambda r=row, c=col: self.cell_clicked(r, c))
                button.grid(row=row, column=col)

    def player_grids(self):
        print("showing grids")
        self.player1_grid = self.create_grid(500, "Player 1 Grid")
      #  self.player2_grid = self.create_grid(600, "Player 2 Grid")

    def cell_clicked(self, row, col):
        print(f"Cell clicked at Row {row}, Column {col}")

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
    

# Create the main application window
main_window = tk.Tk()


# Create an instance of the GUI class
app = GUI(main_window)

app.start_game()


