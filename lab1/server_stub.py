import socket
import selectors
import types
#cd "C:\Users\pfeif\Documents\HAW\S5\VS 2\code\lab1"
#python server_stub.py

host="127.0.0.1"
port=65432
sel = selectors.DefaultSelector()

def start_server(host=host, port=port):
    

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #listening port with TCP
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        #accept connection ohne blocking mit selector
        s.setblocking(False)
        sel.register(s, selectors.EVENT_READ, data=None)
        
        # new
        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            sel.close()
        
        
        
        #old
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received data: {data.decode()}")
                conn.sendall(data)




# add new connection

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

# use existing connection

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


#main
start_server()