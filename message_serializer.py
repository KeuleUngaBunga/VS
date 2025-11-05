import json
import socket
import struct
from typing import Any, Dict

from exception import NetworkException


class MessageSerializer:
    """Handles marshalling/unmarshalling of messages"""

    MESSAGE_HEADER_SIZE = 4  # 4 bytes for message length

    @staticmethod
    def serialize_message(msg: Dict[str, Any]) -> bytes:
        """
        Serialize a message to bytes with length prefix

        Format: [4-byte length][JSON payload]
        """
        json_str = json.dumps(msg, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')

        # Add 4-byte length prefix (big-endian)
        length = len(json_bytes)
        header = struct.pack('>I', length)

        return header + json_bytes

    @staticmethod
    def deserialize_message(data: bytes) -> Dict[str, Any]:
        """
        Deserialize a message from bytes
        Expects format: [4-byte length][JSON payload]
        """
        if len(data) < MessageSerializer.MESSAGE_HEADER_SIZE:
            raise NetworkException("Invalid message: too short")

        try:
            json_str = data.decode('utf-8')
            return json.loads(json_str)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise NetworkException(f"Failed to deserialize message: {e}")

    @staticmethod
    def receive_message(sock: socket.socket) -> Dict[str, Any]:
        """
        Receive a complete message from socket
        Handles the length prefix protocol
        """
        # Read length header
        header = b''
        while len(header) < MessageSerializer.MESSAGE_HEADER_SIZE:
            chunk = sock.recv(MessageSerializer.MESSAGE_HEADER_SIZE - len(header))
            if not chunk:
                raise NetworkException("Connection closed by remote host")
            header += chunk

        # Parse length
        length = struct.unpack('>I', header)[0]

        # Read message body
        body = b''
        while len(body) < length:
            chunk = sock.recv(min(length - len(body), 4096))
            if not chunk:
                raise NetworkException("Connection closed while reading message")
            body += chunk

        return MessageSerializer.deserialize_message(body)

    @staticmethod
    def send_message(sock: socket.socket, msg: Dict[str, Any]) -> None:
        """
        Send a complete message through socket
        """
        data = MessageSerializer.serialize_message(msg)
        sock.sendall(data)

