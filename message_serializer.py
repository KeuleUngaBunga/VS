import json
import socket
import struct
from typing import Any, Dict

from exception import NetworkException


class MessageSerializer:

    MESSAGE_HEADER_SIZE = 4  # 4 bytes for message length

    @staticmethod
    def serialize_message(msg: Dict[str, Any]) -> bytes:
        json_str = json.dumps(msg, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        
        length = len(json_bytes)
        header = struct.pack('>I', length) # Int/4byte big endian

        return header + json_bytes

    @staticmethod
    def deserialize_message(data: bytes) -> Dict[str, Any]:
        if len(data) < MessageSerializer.MESSAGE_HEADER_SIZE:
            raise NetworkException("Invalid message: too short")

        try:
            json_str = data.decode('utf-8')
            return json.loads(json_str)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise NetworkException(f"Failed to deserialize message: {e}")

    @staticmethod
    def receive_message(sock: socket.socket) -> Dict[str, Any]:
        # header
        header = b''
        message = sock.recv(MessageSerializer.MESSAGE_HEADER_SIZE)
        if not message:
            raise NetworkException("Connection closed by remote host")
        header += message

        length = struct.unpack('>I', header)[0] # Int/4byte big endian

        # body
        body = b''
        message = sock.recv(length) 
        if not message:
            raise NetworkException("Connection closed while reading message")
        body += message

        return MessageSerializer.deserialize_message(body)
    

    @staticmethod
    def send_message(sock: socket.socket, msg: Dict[str, Any]) -> None:
        data = MessageSerializer.serialize_message(msg)
        sock.sendall(data)

