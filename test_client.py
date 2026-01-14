import socket
import json
import time

JAVA_HOST = "localhost"
JAVA_PORT = 6000  # muss mit Java RobotNode übereinstimmen

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((JAVA_HOST, JAVA_PORT))
    print("Verbunden mit Java RobotNode")

    messages = [
        {"action": "leftRight", "value": 100},
        {"action": "openClose", "value": 100},
        {"action": "upDown", "value": 0},
    ]

    for msg in messages:
        sock.sendall((json.dumps(msg) + "\n").encode())
        print("Gesendet:", msg)
        time.sleep(1)
