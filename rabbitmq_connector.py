import rabbitpy
import logging

logger = logging.getLogger(__name__)

class RabbitMQConnector:
    def __init__(self, host: str, process_id: int):
        self.host = host
        self.process_id = process_id
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None

    def connect(self):
        self.connection = rabbitpy.Connection(f"amqp://guest:guest@{self.host}:5672/%2F")
        self.channel = self.connection.channel()

        self.exchange = rabbitpy.Exchange(self.channel, "ggt_exchange", "direct")
        self.exchange.declare()

        queue_name = f"ggt_process_{self.process_id}"
        self.queue = rabbitpy.Queue(self.channel, queue_name)
        self.queue.declare()

        self.queue.bind(self.exchange, f"process_{self.process_id}")
        logger.info(f"RabbitMQ ready for process {self.process_id}")

    def cleanup(self):
        try:
            if self.queue:
                self.queue.delete()
            if self.exchange:
                self.exchange.delete()
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
