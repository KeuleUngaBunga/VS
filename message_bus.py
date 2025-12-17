import rabbitpy
import logging

logger = logging.getLogger(__name__)


class MessageBus:
    def __init__(self, connector):
        self.connector = connector

    def send(self, target_id: int, message):
        try:
            msg = rabbitpy.Message(self.connector.channel, message.to_json())
            msg.properties["content_type"] = "application/json"
            msg.publish(self.connector.exchange, f"process_{target_id}")
        except Exception as e:
            logger.error(f"Send error to {target_id}: {e}")
            
    def send_result(self, message):
        try:
            msg = rabbitpy.Message(self.connector.channel, message.to_json())
            msg.properties["content_type"] = "application/json"
            msg.publish(self.connector.exchange, "worker_result")
        except Exception as e:
            logger.error(f"Send error to result: {e}")

    def receive(self):
        if len(self.connector.queue) == 0:
            return None

        msg = self.connector.queue.get()
        if msg:
            data = msg.body.decode("utf-8")
            msg.ack()
            return data
        return None


class AgentMessageBus:
    def __init__(self, connector):
        self.connector = connector

    def send_to_worker(self, agent_id: int, message):
        try:
            msg = rabbitpy.Message(self.connector.worker_result_queue, message.to_json())
            msg.properties["content_type"] = "application/json"
            self.connector.exchange.publish(msg, f"agent_worker_{agent_id}")
        except Exception as e:
            logger.error(f"Send error to agent {agent_id}: {e}")

    def receive_worker_start(self):
        if len(self.connector.worker_queue) == 0:
            return None

        msg = self.connector.worker_queue.get()
        if msg:
            data = msg.body.decode("utf-8")
            msg.ack()
            return data
        return None


class CoordinatorMessageBus:
    def __init__(self, connector):
        self.connector = connector

    def send_to_agent(self, agent_id: int, message):
        try:
            msg = rabbitpy.Message(self.connector.channel, message.to_json())
            msg.properties["content_type"] = "application/json"
            msg.publish(self.connector.exchange, f"agent_worker_{agent_id}")
        except Exception as e:
            logger.error(f"Send error to agent {agent_id}: {e}")

    def receive_agent_register(self):
        if len(self.connector.agent_register_queue) == 0:
            return None

        msg = self.connector.agent_register_queue.get()
        if msg:
            data = msg.body.decode("utf-8")
            msg.ack()
            return data
        return None
    
    def receive_result(self):
        if len(self.connector.worker_result_queue) == 0:
            return None

        msg = self.connector.worker_result_queue.get()
        if msg:
            data = msg.body.decode("utf-8")
            msg.ack()
            return data
        return None