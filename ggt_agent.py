import sys
import subprocess
import logging
import threading
import time

import rabbitpy
from message import AgentRegisterMessage
from message_bus import AgentMessageBus, MessageBus
from message_parser import MessageParser
from process import GGTProcess
from rabbitmq_connector import AgentRabbitMQConnector, RabbitMQConnector

logger = logging.getLogger(__name__)


class GGTAgent:
    def __init__(self, agent_id: int, host: str):
        self.id = agent_id
        self.host = host
        self.connector = AgentRabbitMQConnector(host, agent_id)
        self.bus = AgentMessageBus(self.connector)
        self.running_processes = {}

    def start(self):
        self.connector.connect()
        logger.info(f"Agent {self.id} started, waiting for worker start commands...")
        
        self.register()


        try:
            while True:
                msg_raw = self.bus.receive_worker_start()
                if msg_raw:
                    msg = MessageParser.parse_worker_start(msg_raw)
                    if msg:
                        self.start_worker(msg)

                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info(f"Agent {self.id} shutting down...")
            self.cleanup()

    def register(self):
        """Agent registriert sich beim Coordinator"""
        try:
            msg = AgentRegisterMessage(agent_id=self.id)
            register_msg = rabbitpy.Message(self.connector.channel, msg.to_json())
            register_msg.properties["content_type"] = "application/json"
            register_msg.publish(self.connector.exchange, "agent_register")

            logger.info(f"Agent {self.id}: Registered with coordinator")
        except Exception as e:
            logger.error(f"Agent {self.id}: Registration failed: {e}")


    def start_worker(self, msg):
        
        
        connector = RabbitMQConnector(self.host, msg.process_id)
        bus = MessageBus(connector)
        
        process = GGTProcess(msg.process_id, msg.initial_value, msg.pred, msg.succ, connector, bus) 
        thread = threading.Thread(target=process.start, daemon=True)
        thread.start()

        logger.info(f"Agent {self.id}: Starting worker {msg.process_id}")
        self.running_processes[msg.process_id] = process
        
        

    def cleanup(self):
        for pid, proc in self.running_processes.items():
            logger.info(f"Agent {self.id}: Terminating worker {pid}")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

        self.connector.cleanup()


def main():
    if len(sys.argv) < 2:
        print("Usage: ggt_agent.py <agent_id> [host]")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    agent_id = int(sys.argv[1])
    host = sys.argv[2] if len(sys.argv) > 2 else "localhost"

    agent = GGTAgent(agent_id, host)
    agent.start()


if __name__ == "__main__":
    main()
