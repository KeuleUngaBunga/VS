import socket
import threading
from datastore import Datastore
from exception import NetworkException
from message_serializer import MessageSerializer
from serverstub import ServerStub


class RPCServer:

    def __init__(self, host: str, port: int, impl: Datastore):
        self.host = host
        self.port = port
        self.stub = ServerStub(impl)
        self.running = False

    def start(self) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            print(f"RPC Server listening on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    print(f"Client connected from {client_addr}")

                    # Handle client in thread
                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_addr)
                    )
                    thread.daemon = True
                    thread.start()

                except KeyboardInterrupt:
                    break

        finally:
            self.stop()

    def _handle_client(self, client_socket: socket.socket, client_addr: tuple) -> None:
        try:
            while True:
                request = MessageSerializer.receive_message(client_socket)
                response = self.stub.dispatch(request)
                MessageSerializer.send_message(client_socket, response)

        except NetworkException as e:
            print(f"Network error from {client_addr}: {e}")
        except Exception as e:
            print(f"Error handling client {client_addr}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            print(f"Client {client_addr} disconnected")

    def stop(self) -> None:
        self.running = False
        try:
            self.server_socket.close()
        except:
            pass
        print("RPC Server stopped")