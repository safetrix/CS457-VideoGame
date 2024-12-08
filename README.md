# CS457-VideoGame
Project for CS457 Computer Networks and the Internet

This is going to be a simple implementation of the classic battleship game
**How to play:**
1. Launch server.py and two instances of client.py
2. Both clients press start game and must wait till both clients connect
3. A new screen with ask for username input
4. Client designs a game board by selecting the ship type using the buttons on the right and selecting a tile on the 10 x 10 grid. Ships can be rotated by pressing 'R' on the keyboard
5. Once all ships are placed the 'Ready' button can be clicked, which will then save the game board and start the game
6. Each player takes turns selecting a tile on the grid and attacking, game continues until all ships have been sunk by an opposing player

**Technologies used:**
* Python
* Sockets
* Tkinter Library

**Additional resources:**
* [[Link to Python documentation](https://docs.python.org/3/library/tk.html)]
* [[Link to sockets tutorial](https://docs.python.org/3/howto/sockets.html)]

**Security/Risk Evaluation:**

There are multiple inherent security risks associated with this multiplayer game. First, there is potentially no limit to the length of a message that one player can send to the other, which could be used to cause a buffer overflow and potentially harm the other player or server hosting the game. Some testing found that there was some form of message length limiting present in our current system, however, we did not test a full range of characters and message lengths. Secondly, both connections are unencrypted and the IPs of both players are kept within the log file, meaning if a player or third party gained access to this file they would be able to find the IPs of both players. This could be avoided by encrypting the IPs of both players or the log file itself. With the way the game functions now, both players must know the IP address and the specific port that the server is broadcasting to, which in a final public implementation of this game this would be changed as that would introduce a broad number of security risks to the server/servers hosting the game. This would require a lot of changes to how the game is run and connects to the server, however, it could be done by changing the server so that it broadcasts the available lobby to any potential users on the network, then the GUI allows the users to find this lobby (potentially in a list of lobbies) and join rather than inputting the server IP and port manually in the command line.

**What went well:**
Throughout our project there were many highpoints and things we did well. Through the planning process, we had a very consise and realistic goal, creating a battleship game with a GUI. This goal was well broken into the sprints allocated and properly executed within each iteration. I feel the best of this project comes from the game logic and minimalistic UI we created. This boils down to the grid functionality, the chat, and the clear labels the indicate whats currently happening in the game. Often games feel cluterred and overwhelming, our end product did a great job at avoiding this and in return our game is playable to those who have never touched battleship before. i would also say we did a great job splitting up our tasking, as Zach did all of the game logic and communication of moves back and forth. Brice spent most of his time creating the GUI process before and after the game is initiated and finished, along with all of the chat functionality and GUI. These two tasks were well merged together, as we had minimal merge conflicts and code bugs when bringing our code in together. Overall, we are very pleased with this outcome, and would like to add more functionlity such as: additional bug testing, game noises, improved ship icons, game history, personal accounts, and possibly encryption to make sure cheating and attack vectors arent possible. 


**What could be improved on:**
In retrospective there werent too many things we feel we could have done better. When looking at the code, most of the function is within the GUI.py class, which can make code interpretation very hard. In the future, with more OOP practice in python, we may have created mulitple classes and files that could better split up our game. This would make debugging, code redability, and future implementations much easier. Another thing we could improve on are some of the bugs within the game, which may be a product of Tkinter library limitations. There are some bugs within the attack functionality, which could in turn make for an unfair game. Knowing more about Tkinter and possibly implementing better code practice in games could fix these issues, which came from a lack of experience on our parts. Overall, we did a great job with this project, but other fixes such as Encryption, bugs, terminal output, UI fixes, and Tkinter logic could ave made the process smoother and the end product slightly better!

