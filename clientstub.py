import socket
from typing import Any

from datastore import Datastore
from exception import NetworkException, RemoteException
from message_serializer import MessageSerializer


class ClientStub:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.request_counter = 0
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

    def execute(self, method: str, *args, **kwargs) -> Any:
        self.connect()

        try:
            request_id = self.request_counter
            self.request_counter += 1

            request = {
                "type": "request",
                "method": method,
                "args": list(args),
                "kwargs": kwargs,
                "request_id": request_id
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

    def __init__(self, client_stub: ClientStub):
        self.client_stub = client_stub

    def write(self, index: int, data: str) -> None:
        self.client_stub.execute("write", index, data)

    def read(self, index: int) -> str:
        return self.client_stub.execute("read", index)