import sys
import logging
import time
from message_bus import CoordinatorMessageBus
from message_parser import MessageParser
from message import AgentRegisterMessage, WorkerStartMessage
from rabbitmq_connector import CoordinatorRabbitMQConnector

logger = logging.getLogger(__name__)


class GGTCoordinator:
    def __init__(self, host: str):
        self.host = host
        self.connector = CoordinatorRabbitMQConnector(host)
        self.bus = CoordinatorMessageBus(self.connector)
        self.agents = []
        self.next_agent_idx = 0
        self.results = {}

    def start(self):
        self.connector.connect()
        logger.info("Coordinator started")

        import threading
        register_thread = threading.Thread(target=self.listen_for_agents, daemon=True)
        register_thread.start()

        try:
            self.cli_loop()
        except KeyboardInterrupt:
            logger.info("Coordinator shutting down...")
            self.cleanup()

    def listen_for_agents(self):
        while True:
            msg_raw = self.bus.receive_agent_register()
            if msg_raw:
                msg = MessageParser.parse_agent_register(msg_raw)
                if msg:
                    if msg.agent_id not in self.agents:
                        self.agents.append(msg.agent_id)
                        logger.info(f"Agent {msg.agent_id} registered. Total agents: {len(self.agents)}")

            time.sleep(0.1)

    def cli_loop(self):
        print("\n=== GGT Coordinator ===")
        print("Commands:")
        print("  start <values> - e.g., 'start 15 20 25' starts GGT with 3 processes")
        print("  status - show registered agents")
        print("  exit - shutdown")
        print()

        while True:
            try:
                cmd = input("coordinator> ").strip()

                if cmd.startswith("start "):
                    values = list(map(int, cmd.split()[1:]))
                    self.start_ggt(values)
                    
                    time.sleep(30)
                    msg_raw = self.bus.receive_result()
                    print(f"{msg_raw}")
                    

                elif cmd == "status":
                    print(f"Registered agents: {self.agents}")
                    print(f"Total: {len(self.agents)}")

                elif cmd == "exit":
                    break

            except Exception as e:
                print(f"Error: {e}")

    def start_ggt(self, values):
        if not self.agents:
            print("No agents registered!")
            return

        n = len(values)
        print(f"Starting GGT with {n} processes on {len(self.agents)} agents...")

        for i, val in enumerate(values):
            pred = i - 1
            succ = (i + 1) % n
            agent_id = self.agents[self.next_agent_idx % len(self.agents)]

            msg = WorkerStartMessage(
                process_id=i,
                initial_value=val,
                pred=pred,
                succ=succ
            )

            logger.info(f"Sending worker start to agent {agent_id}: process_id={i}, value={val}")
            self.bus.send_to_agent(agent_id, msg)
            self.next_agent_idx += 1

        print(f"GGT started with values: {values}")

    def cleanup(self):
        self.connector.cleanup()


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    coordinator = GGTCoordinator(host)
    coordinator.start()


if __name__ == "__main__":
    main()

