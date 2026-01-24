import socket
from typing import Any, List, Tuple

from datastore import Datastore
from exception import NetworkException, RemoteException
from message_serializer import MessageSerializer


class ReplicatedClientStub:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self) -> None:
        if self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 tcp socket
                self.sock.connect((self.host, self.port))
            except socket.error as e:
                raise NetworkException(f"Failed to connect to {self.host}:{self.port}: {e}")

    def disconnect(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def execute(self, method: str, *args) -> Any:
        self.connect()

        try:
            request = {
                "type": "request",
                "method": method,
                "args": list(args),
            }

            MessageSerializer.send_message(self.sock, request)

            response = MessageSerializer.receive_message(self.sock)

            if response.get("status") == "error":
                error_msg = response.get("message", "Unknown error")
                error_type = response.get("error", "RemoteException")
                raise RemoteException(f"{error_type}: {error_msg}")

            if response.get("status") != "success":
                raise RemoteException("Invalid response from server")

            return response.get("result")

        except NetworkException:
            raise
        except RemoteException:
            raise
        except Exception as e:
            raise NetworkException(f"Communication error: {e}")

    def close(self) -> None:
        self.disconnect()


class DatastoreStub(Datastore):

    def __init__(self, servers: list[tuple[str, int]]):
        self.clients = [
            ReplicatedClientStub(host, port) for host, port in servers
        ]
        self._rr_index = 0
        
    
    
    def write(self, index: int, data: str) -> None:
        failed = []

        for client in self.clients:
            try:
                client.execute("write", index, data)
            except NetworkException:
                failed.append(client)
            except RemoteException:
                failed.append(client)

        for f in failed:
            if f in self.clients:
                self.clients.remove(f)

        if not self.clients:
            raise NetworkException("Keine Server")


    def read(self, index: int) -> str:
        if not self.clients:
            raise NetworkException("Keine Server")

        attempts = len(self.clients)
        self._rr_index = 0
        for _ in range(attempts):
            client = self.clients[self._rr_index]
            self._rr_index = (self._rr_index + 1) % len(self.clients)

            try:
                return client.execute("read", index)
            except NetworkException:
                self.clients.remove(client)
            except RemoteException:
                raise

        raise NetworkException("Keine Server")
    
    def close(self):
        for client in self.clients:
            client.close()
