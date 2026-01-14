import socket
import json

HOST = "localhost"
PORT = 7000

robots = {}  # name -> {ip, port}

def handle_client(conn, addr):
    print("Verbunden:", addr)
    buffer = ""

    while True:
        data = conn.recv(1024)
        if not data:
            break

        buffer += data.decode()

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            msg = json.loads(line)

            msg_type = msg.get("type")

            if msg_type == "register":
                name = msg["name"]
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
