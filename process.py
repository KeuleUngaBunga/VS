import time
import datetime
import logging
from algorithm import GGTAlgorithm
from message_parser import MessageParser
from message import GGTMessage

logger = logging.getLogger(__name__)

class GGTProcess:
    def __init__(self, process_id, initial_value, predecessor_id, successor_id, connector, bus):
        self.id = process_id
        self.predecessor = predecessor_id
        self.successor = successor_id
        self.algorithm = GGTAlgorithm(initial_value)
        self.bus = bus
        self.connector = connector
        self.is_running = True

    def start(self, initial_wait=15, convergence_time=60):
        self.connector.connect()

        logger.info(f"Process {self.id}: Waiting {initial_wait}s for others...")
        time.sleep(initial_wait)

        logger.info(f"Process {self.id}: Starting with M={self.algorithm.M}")
        self.broadcast_value()

        start = datetime.datetime.now()

        while self.is_running:
            incoming_raw = self.bus.receive()
            if incoming_raw:
                msg = MessageParser.parse(incoming_raw)
                if msg:
                    changed = self.algorithm.update_value(msg.value)
                    if changed:
                        logger.info(f"Process {self.id}: M updated to {self.algorithm.M}")
                        self.broadcast_value()

            if (datetime.datetime.now() - start).total_seconds() > convergence_time:
                break

            time.sleep(0.01)

        logger.info(f"Process {self.id}: Finished with M={self.algorithm.M}")
        self.connector.cleanup()

    def broadcast_value(self):
        m = self.algorithm.M
        msg = GGTMessage(sender_id=self.id, value=m)
        self.bus.send(self.predecessor, msg)
        self.bus.send(self.successor, msg)
