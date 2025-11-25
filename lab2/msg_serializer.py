import json
from typing import Any, Dict, List, Optional


class connect_decoder():

        #def __init__(self):

        @staticmethod
        def encode_register(client_id: str, client_queue: str) -> bytes:
                """Create a registration message (JSON bytes) for a client.

                Message format:
                    {
                        "type": "register",
                        "client_id": "client_1",
                        "client_queue": "client_client_1",
                    }
                """
                payload = {
                        "type": "register",
                        "client_id": client_id,
                        "client_queue": client_queue,
                }
                return json.dumps(payload).encode('utf-8')

        @staticmethod
        def encode_spawn_nodes(client_id: str, node_ids: List[int], node_vals: List[int], total_nodes: int) -> bytes:
                """Create a spawn_nodes command for a specific client.

                Message format:
                    {
                        "type": "spawn_nodes",
                        "client_id": "client_1",
                        "node_ids": [0,1,2],
                        "total_nodes": 12
                    }
                """
                payload = {
                        "type": "spawn_nodes",
                        "client_id": client_id,
                        "node_ids": node_ids,
                        "node_vals": node_vals,
                        "total_nodes": total_nodes,
                }
                return json.dumps(payload).encode('utf-8')

        

        def decode(self, data:bytes) -> Dict[str, Any]:
                """Decode the stored bytes as JSON and return the dict."""
                try:
                        return json.loads(data.decode('utf-8'))
                except Exception:
                        return {}



class node_decoder():
        
        @staticmethod
        def encode(node_id: int, value: Any) -> bytes:
                """Encode a node message containing a node id and a value into JSON bytes.

                Message format:
                    {
                        "type": "node_message",
                        "node_id": 3,
                        "value": 42
                    }
                """
                payload = {
                        "type": "node_message",
                        "node_id": node_id,
                        "value": value,
                }
                return json.dumps(payload).encode('utf-8')

        def decode(self, data:bytes) -> Dict[str, Any]:
                """Decode the stored bytes as JSON and return the dict."""
                try:
                        return json.loads(data.decode('utf-8'))
                except Exception:
                        return {}