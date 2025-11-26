import json
import time
from venv import logger


class MessageParser:  
    def create_message(self, message_type: str, value: int) -> str:
        message = {
            'type': message_type,
            'sender_id': self.process_id,
            'value': value,
            'iteration': self.iteration,
            'timestamp': time.time()
        }
        return json.dumps(message)

    def parse_message(self, message_body: str) -> dict:
        try:
            return json.loads(message_body)
        except json.JSONDecodeError as e:
            logger.error(f'Process {self.process_id}: Failed to parse message: {e}')
            return None