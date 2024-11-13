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
        self.menu.add_command(label="Borderless Window", command=lambda: self.option_selected("Borderless Window"))
        self.menu.add_command(label="Open Chat", command=lambda: self.option_selected("Open Chat"))
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
            name = name_entry.get()
            print(f"Name entered: {name}")
            # Hide name entry components
            name_label.place_forget()
            name_entry.place_forget()
            submit_button.place_forget()

            # Show confirmation label
            self.confirmation_label = tk.Label(self.main_window, text=f"Welcome, {name}!\nWaiting for other player to join...", font=("Helvetica", 24))
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
        frame.place(relx=x_position, rely=0.5, anchor="center")

        # Create the grid label
        grid_label = tk.Label(frame, text=title, font=("Helvetica", 24))
        grid_label.grid(row=0, column=0, columnspan=10)

        # Create a 10x10 grid of buttons (representing the game cells)
        grid_buttons = []
        for i in range(10):
            row = []
            for j in range(10):
                button = tk.Button(frame, text="", width=4, height=2, relief="solid", command=lambda i=i, j=j: self.cell_clicked(i, j))
                button.grid(row=i+1, column=j)
                row.append(button)
            grid_buttons.append(row)

        return grid_buttons

    def player_grids(self):
        print("showing grids")
        self.player1_grid = self.create_grid(500, "Player 1 Grid")
      #  self.player2_grid = self.create_grid(600, "Player 2 Grid")

    def cell_clicked(self, row, col):
        print(f"Cell clicked at Row {row}, Column {col}")


# Create the main application window
main_window = tk.Tk()

# Create an instance of the GUI class
app = GUI(main_window)

app.start_game()


