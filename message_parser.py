from message import GGTMessage
import json
import logging

logger = logging.getLogger(__name__)

class MessageParser:
    @staticmethod
    def parse(raw: str):
        try:
            return GGTMessage.from_json(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
            return None
