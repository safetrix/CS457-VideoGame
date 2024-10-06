
import socket
import logging

logging.basicConfig(filename = 'client_connections.log', level = logging.INFO)
def start_connection(host, port):
    addr = (host, port)

    try:
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"connection created: {addr}")
        sock.setblocking(True)
        sock.connect((host,port))
    
        message = sock.recv(1024).decode()
        print(message)
        sock.send(b"ready")

    except Exception as e:
        print("Error: ", e)
        logging.error("Error in connection attempt: ", e)

#events = selectors.EVENT_READ | selectors.EVENT_WRITE
#message = libclient.Message(sel, sock, addr, request)
#sel.register(sock, events, data=message)

    
start_connection("127.0.0.1", 65432)
