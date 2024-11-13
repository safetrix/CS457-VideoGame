import tkinter as tk


def option_selected(option): #this can be implemented later to send data on which button was clicked
    print(f"{option} selected!")

def open_name_window():
    start_button.place_forget()
    quit_button.place_forget()

    name_label = tk.Label(main_window, text="Enter your name:", font=("Helvetica", 24))
    name_label.place(relx =.5, rely=.45, anchor = "center")

    # Create an Entry widget to input the name
    name_entry = tk.Entry(main_window, font=("Helvetica", 24), justify="center")
    name_entry.place(relx=.5, rely=.5, anchor = "center")

    def submit_name():
        name = name_entry.get()
        print(f"Name entered: {name}")
        # You can do something with the name here, like transitioning to the next screen
        name_label.place_forget()
        name_entry.place_forget()
        submit_button.place_forget()

        # Optionally, display a confirmation or continue with the next step
        confirmation_label = tk.Label(main_window, text=f"Welcome, {name}!\n Waiting for other player to join...", font=("Helvetica", 24))
        confirmation_label.place(relx = .5, rely = .5, anchor = "center")
    submit_button = tk.Button(main_window, text="Submit", font=("Helvetica", 14), command=submit_name)
    submit_button.place(relx=.5, rely =.55, anchor= "center")


main_window = tk.Tk()
main_window.title("BattleShip")
main_window.attributes("-fullscreen", True)



start_button = tk.Button(main_window, text = "Start Game", font=("Helvectica", 24), width = 10, height = 2, relief="solid", padx=10, pady=5, command=open_name_window)
start_button.place(relx =0.5, rely=0.5, anchor = "center")


quit_button = tk.Button(main_window, text = "Quit", font =("Helvectica", 24), width = 10, height = 2, relief="solid", padx=10, pady=5, command=main_window.quit)
quit_button.place(relx =0.5, rely=0.55, anchor = "center")

options_label = tk.Label(main_window, text = "Options", font = ("Helvectica", 18), borderwidth=2, relief="solid", padx=10, pady=5)
options_label.place(x=10,y=10)

#Menu for the options below

menu = tk.Menu(main_window, tearoff=0)
menu.add_command(label="Borderless Window", command=lambda: option_selected("Borderless Window"))
menu.add_command(label="Open Chat", command=lambda: option_selected("Open Chat"))
menu.add_command(label="Quit", command=main_window.quit)

#def function for menu

def menu_show(event):
     # Get the position and size of the "Options" label
    menu.post(event.x_root, event.y_root)

options_label.bind("<Button-1>", menu_show)



main_window.mainloop()

