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


class AgentRabbitMQConnector:
    def __init__(self, host: str, agent_id: int):
        self.host = host
        self.agent_id = agent_id
        self.connection = None
        self.channel = None
        self.exchange = None
        self.worker_queue = None

    def connect(self):
        self.connection = rabbitpy.Connection(f"amqp://guest:guest@{self.host}:5672/%2F")
        self.channel = self.connection.channel()

        self.exchange = rabbitpy.Exchange(self.channel, "ggt_exchange", "direct")
        self.exchange.declare()

        worker_queue_name = f"agent_worker_queue_{self.agent_id}"
        self.worker_queue = rabbitpy.Queue(self.channel, worker_queue_name)
        self.worker_queue.declare()
        self.worker_queue.bind(self.exchange, f"agent_worker_{self.agent_id}")

        logger.info(f"Agent {self.agent_id} connected to RabbitMQ")

    def cleanup(self):
        try:
            if self.worker_queue:
                self.worker_queue.delete()
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"Agent cleanup failed: {e}")


class CoordinatorRabbitMQConnector:
    def __init__(self, host: str):
        self.host = host
        self.connection = None
        self.channel = None
        self.exchange = None
        self.agent_register_queue = None
        self.worker_result_queue = None

    def connect(self):
        self.connection = rabbitpy.Connection(f"amqp://guest:guest@{self.host}:5672/%2F")
        self.channel = self.connection.channel()

        self.exchange = rabbitpy.Exchange(self.channel, "ggt_exchange", "direct")
        self.exchange.declare()

        self.agent_register_queue = rabbitpy.Queue(self.channel, "coordinator_agent_register")
        self.agent_register_queue.declare()
        self.agent_register_queue.bind(self.exchange, "agent_register")
        
        self.worker_result_queue = rabbitpy.Queue(self.channel, "coordinator_worker_result")
        self.worker_result_queue.declare()
        self.worker_result_queue.bind(self.exchange, "worker_result")

        logger.info("Coordinator connected to RabbitMQ")

    def cleanup(self):
        try:
            if self.agent_register_queue:
                self.agent_register_queue.delete()
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
            if self.worker_result_queue:
                self.worker_result_queue.delete()
        except Exception as e:
            logger.error(f"Coordinator cleanup failed: {e}")