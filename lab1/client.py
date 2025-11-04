#simple client
import socket
import selectors
import types
import client_stub as cs

#python client.py


#main
run=True
while run:
    print("Client is running. Press Ctrl+C to stop.")
    print("How many connections to start? or 'q' to quit:")
    cons=input()
    #process input, possibly add msgs later
    if cons.lower()=='q':
        run=False
    elif cons.isdigit():
        cs.start_connections(num_conns= int(cons))
    else:
        print("Please enter a valid number.")
        continue

print("Shutting down client.")