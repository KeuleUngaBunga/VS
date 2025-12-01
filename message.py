import json
import time

class GGTMessage:
    def __init__(self, sender_id: int, value: int, msg_type: str = "value"):
        self.sender_id = sender_id
        self.value = value
        self.type = msg_type
        self.timestamp = time.time()

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(text: str):
        data = json.loads(text)
        return GGTMessage(
            sender_id=data["sender_id"],
            value=data["value"],
            msg_type=data["type"],
        )
