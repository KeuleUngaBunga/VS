import rabbitpy
import logging
from message import GGTMessage

logger = logging.getLogger(__name__)

class MessageBus:
    def __init__(self, connector):
        self.connector = connector

    def send(self, target_id: int, message: GGTMessage):
        try:
            msg = rabbitpy.Message(self.connector.channel, message.to_json())
            msg.properties["content_type"] = "application/json"
            msg.publish(self.connector.exchange, f"process_{target_id}")
        except Exception as e:
            logger.error(f"Send error to {target_id}: {e}")

    def receive(self):
        if len(self.connector.queue) == 0:
            return None

        msg = self.connector.queue.get()
        if msg:
            data = msg.body.decode("utf-8")
            msg.ack()
            return data
        return None
