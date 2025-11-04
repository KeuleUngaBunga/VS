
import sys
import socket
import selectors
import types
#console
#python client_stub.py

host="127.0.0.1"
port=65432

#simple client function
def start_client(host=host, port=port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #connect to server
        s.connect((host, port))
        message = "Hello, Server!"
        print(f"Sending data: {message}")
        s.sendall(message.encode())
        data = s.recv(1024)
        print(f"Received data: {data.decode()}")


#advanced client with selectors
sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

def start_connections(num_conns, host=host, port=port):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)

# ...
#main
#start_client()
"""
run=True
while run:
    print("Client is running. Press Ctrl+C to stop.")
    print("How many connections to start? or 'q' to quit:")
    cons=input()
    #process input, possibly add msgs later
    if cons.lower()=='q':
        run=False
    elif cons.isdigit():
        start_connections(host, port, int(cons))
    else:
        print("Please enter a valid number.")
        continue

print("Shutting down client.")
"""