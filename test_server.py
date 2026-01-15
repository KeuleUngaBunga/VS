import socket
import json

HOST = "localhost"
PORT = 6000

robots = {}  # name -> {ip, port}

def handle_client(conn, addr):
    print("Verbunden:", addr)
    buffer = ""

    data = conn.recv(1024)
    if not data:
        return

    buffer += data.decode()

    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        msg = json.loads(line)

        msg_type = msg.get("type")

        if msg_type == "register":
            name = msg["name"]


            if(name in robots):
                print(f"Aktueller registrierter Roboter: {name}")
                response = {
                    "status": "error",
                    "message": "robot already registered"
                }
            else:
                robots[name] = {
                "ip": msg["ip"],
                "port": msg["port"]
                }
                print(f"REGISTER: {name} @ {robots[name]}")

                response = {
                    "status": "ok",
                    "message": "registered successfully"
                }
            conn.sendall((json.dumps(response) + "\n").encode())

        elif msg_type == "heartbeat":
            print(f"HEARTBEAT von {msg['name']}")
            response = {
                "status": "ok",
                "message": "heartbeat received"
            }
            conn.sendall((json.dumps(response) + "\n").encode())
        elif msg_type == "unregister":
            name = msg["name"]
            if name in robots:
                del robots[name]
                print(f"UNREGISTER: {name}")
                response = {
                    "status": "ok",
                    "message": "unregistered successfully"
                }
            else:
                response = {
                    "status": "error",
                    "message": "robot not found"
                }
            conn.sendall((json.dumps(response) + "\n").encode())
        else:
            print("Unbekannte Nachricht:", msg)

    print("Verbindung beendet:", addr)


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Python Server läuft auf {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    start_server()
