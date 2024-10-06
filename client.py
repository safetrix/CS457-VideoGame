import socket



def start_connection(host, port):
    addr = (host, port)

    try:
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(True)
        sock.connect((host,port))
        sock.send(b"test")
    
       
        message = sock.recv(1024).decode()
        print("got back message: ", message)
    except Exception as e:
        print("Error: ", e)
#events = selectors.EVENT_READ | selectors.EVENT_WRITE
#message = libclient.Message(sel, sock, addr, request)
#sel.register(sock, events, data=message)

    
start_connection("127.0.0.1", 65432)
