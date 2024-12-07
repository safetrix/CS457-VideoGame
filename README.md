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
