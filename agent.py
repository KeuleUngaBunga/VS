import logging
from queue import Queue
import time
import threading
from typing import Dict

from rabbitmq_connector import RabbitMQConnector
from message import (
    AgentRegisterMessage,
    AgentHeartbeatMessage,
    GGTValueMessage,
    StartProcessMessage,
    ProcessCompleteMessage,
    Message
)
from process import GGTProcess

logger = logging.getLogger(__name__)


class Agent:

    def __init__(
        self,
        agent_id: int,
        coordinator_id: int = 0,
        capacity: int = 10,
        host: str = "localhost"
        
    ):
        self.id = agent_id
        self.coordinator_id = coordinator_id
        self.capacity = capacity
        self.host = host

        self.connector: RabbitMQConnector | None = None

        self.processes: Dict[int, GGTProcess] = {}
        self.process_threads: Dict[int, threading.Thread] = {}

        self.is_running = False
        self.last_heartbeat = 0.0
        self.heartbeat_interval = 2.0  # Sekunden
        self.process_inboxes: Dict[int, Queue] = {}
        self.process_outbox = Queue()

    # ------------------------------------------------------------

    def start(self):
        try:
            self.connector = RabbitMQConnector(
                host=self.host,
                role="agent",
                component_id=self.id
            )
            self.connector.connect()

            self.is_running = True
            logger.info(f"Agent {self.id} started")

            self.register_with_coordinator()
            self.message_loop()

        except Exception as e:
            logger.error(f"Agent {self.id} startup failed: {e}")
            self.cleanup()
            raise

    # ------------------------------------------------------------

    def register_with_coordinator(self):
        msg = AgentRegisterMessage(self.id, self.capacity)
        self.connector.send(
            f"coordinator_{self.coordinator_id}",
            msg.to_json()
        )
        logger.info(
            f"Agent {self.id}: Registered with Coordinator {self.coordinator_id}"
        )

    # ------------------------------------------------------------

    def message_loop(self):
        while self.is_running:
            try:
                raw_msg = self.connector.receive()

                if raw_msg:
                    msg = Message.from_json(raw_msg)

                    if isinstance(msg, StartProcessMessage):
                        self.handle_start_process(msg)
                    else:
                        logger.warning(
                            f"Agent {self.id}: Unknown message {type(msg)}"
                        )
                self._dispatch_process_messages()

                self._maybe_send_heartbeat()
                time.sleep(0.05)

            except Exception as e:
                logger.error(f"Agent {self.id} message loop error: {e}")
                
                
    def _dispatch_process_messages(self):
        while not self.process_outbox.empty():
            sender_pid, value = self.process_outbox.get()

            msg = GGTValueMessage(sender_pid, value)

            # an alle anderen Prozesse weiterleiten
            for pid, inbox in self.process_inboxes.items():
                if pid != sender_pid:
                    inbox.put((sender_pid, value))

    # ------------------------------------------------------------

    def handle_start_process(self, msg: StartProcessMessage):
        pid = msg.process_id

        if pid in self.processes:
            logger.warning(
                f"Agent {self.id}: Process {pid} already running"
            )
            return

        if len(self.processes) >= self.capacity:
            logger.warning(
                f"Agent {self.id}: Capacity reached ({self.capacity})"
            )
            return

        logger.info(
            f"Agent {self.id}: Starting process {pid} (M={msg.initial_value})"
        )

        inbox = Queue()
        self.process_inboxes[pid] = inbox

        process = GGTProcess(
            process_id=pid,
            initial_value=msg.initial_value,
            inbox=inbox,
            outbox=self.process_outbox
)

        self.processes[pid] = process

        thread = threading.Thread(
            target=self._run_process,
            args=(process,),
            daemon=True
        )
        thread.start()
        self.process_threads[pid] = thread

    # ------------------------------------------------------------

    def _run_process(self, process: GGTProcess):
        try:
            process.start()
            result = process.get_result()

            logger.info(
                f"Agent {self.id}: Process {process.id} finished (M={result})"
            )

            self.report_process_complete(process.id, result)

        except Exception as e:
            logger.error(
                f"Agent {self.id}: Process {process.id} failed: {e}"
            )

        finally:
            self.processes.pop(process.id, None)
            self.process_threads.pop(process.id, None)

    # ------------------------------------------------------------

    def _maybe_send_heartbeat(self):
        now = time.time()
        if now - self.last_heartbeat >= self.heartbeat_interval:
            self.last_heartbeat = now
            msg = AgentHeartbeatMessage(
                self.id,
                len(self.processes)
            )
            self.connector.send(
                f"coordinator_{self.coordinator_id}",
                msg.to_json()
            )

    # ------------------------------------------------------------

    def report_process_complete(self, process_id: int, final_value: int):
        msg = ProcessCompleteMessage(
            self.id,
            process_id,
            final_value
        )
        self.connector.send(
            f"coordinator_{self.coordinator_id}",
            msg.to_json()
        )

    # ------------------------------------------------------------

    def cleanup(self):
        self.is_running = False

        for process in list(self.processes.values()):
            process.stop()

        for thread in self.process_threads.values():
            thread.join(timeout=2)

        if self.connector:
            self.connector.cleanup()

        logger.info(f"Agent {self.id}: Cleanup complete")
        
def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: agent.py <agent_id> [coordinator_id] [capacity] [host]")
        print("Example: agent.py 1 0 10 localhost")
        sys.exit(1)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    agent_id = int(sys.argv[1])
    coordinator_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    capacity = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    host = sys.argv[4] if len(sys.argv) > 4 else "localhost"
    
    agent = Agent(agent_id, coordinator_id, capacity, host)
    
    try:
        agent.start()
    except KeyboardInterrupt:
        logger.info(f"Agent {agent_id}: Shutdown requested")
        agent.cleanup()


if __name__ == "__main__":
    main()


# import logging
# import time
# import threading
# from typing import Dict, List
# from rabbitmq_connector import RabbitMQConnector
# from message import (
#     AgentRegisterMessage, AgentHeartbeatMessage, 
#     StartProcessMessage, ProcessCompleteMessage, Message
# )
# from process import GGTProcess

# logger = logging.getLogger(__name__)


# class Agent:
        
#     def __init__(self, agent_id: int, coordinator_id: int = 0, 
#                  capacity: int = 10, host: str = "localhost"):
#         self.id = agent_id
#         self.coordinator_id = coordinator_id
#         self.capacity = capacity
#         self.host = host
        
#         self.connector = None
#         self.processes: Dict[int, GGTProcess] = {}
#         self.process_threads: Dict[int, threading.Thread] = {}
#         self.is_running = False

#     def start(self):
#         """Starte den Agent"""
#         try:
#             # Verbinde zu RabbitMQ
#             self.connector = RabbitMQConnector(self.host, self.id, "agent")
#             self.connector.connect()
            
#             self.is_running = True
#             logger.info(f"Agent {self.id} started")
            
#             # Registriere beim Coordinator
#             self.register_with_coordinator()
            
#             # Starte Message-Loop
#             self.message_loop()
            
#         except Exception as e:
#             logger.error(f"Agent {self.id} startup failed: {e}")
#             self.cleanup()
#             raise

#     def register_with_coordinator(self):
#         """Registriere diesen Agent beim Coordinator"""
#         msg = AgentRegisterMessage(self.id, self.capacity)
#         self.connector.send(f"coordinator_{self.coordinator_id}", msg.to_json())
#         logger.info(f"Agent {self.id}: Registered with Coordinator {self.coordinator_id}")

#     def message_loop(self):
#         """Hauptschleife für Message-Verarbeitung"""
#         while self.is_running:
#             try:
#                 # Versuche, eine Nachricht zu empfangen
#                 raw_msg = self.connector.receive()
                
#                 if raw_msg:
#                     msg = Message.from_json(raw_msg)
                    
#                     if isinstance(msg, StartProcessMessage):
#                         self.handle_start_process(msg)
#                     else:
#                         logger.warning(f"Agent {self.id}: Unknown message type: {type(msg)}")
                
#                 # Sende Heartbeat
#                 if len(self.process_threads) > 0:
#                     self.send_heartbeat()
                
#                 time.sleep(0.1)
                
#             except Exception as e:
#                 logger.error(f"Agent {self.id} message loop error: {e}")

#     def handle_start_process(self, msg: StartProcessMessage):
#         """Verarbeite den Befehl zum Starten eines Prozesses"""
#         process_id = msg.process_id
        
#         if process_id in self.processes:
#             logger.warning(f"Agent {self.id}: Process {process_id} already exists")
#             return
        
#         if len(self.processes) >= self.capacity:
#             logger.warning(f"Agent {self.id}: Capacity reached, cannot start process {process_id}")
#             return
        
#         logger.info(f"Agent {self.id}: Starting process {process_id} with M={msg.initial_value}")
        
#         # Erstelle Prozess
#         process = GGTProcess(
#             process_id=process_id,
#             initial_value=msg.initial_value,
#             predecessor_id=msg.predecessor_id,
#             successor_id=msg.successor_id,
#             connector=self.connector,
#             agent_id=self.id
#         )
        
#         self.processes[process_id] = process
        
#         # Starte Prozess in eigenem Thread
#         thread = threading.Thread(
#             target=self._run_process,
#             args=(process,),
#             daemon=True
#         )
#         thread.start()
#         self.process_threads[process_id] = thread
        
#         logger.info(f"Agent {self.id}: Process {process_id} thread started")

#     def _run_process(self, process: GGTProcess):
#         """Führe einen GGT-Prozess aus (in eigenem Thread)"""
#         try:
#             process.start()
            
#             # Prozess abgeschlossen
#             result = process.get_result()
#             logger.info(f"Agent {self.id}: Process {process.id} finished with result M={result}")
            
#             # Melde Abschluss dem Coordinator
#             self.report_process_complete(process.id, result)
            
#         except Exception as e:
#             logger.error(f"Agent {self.id}: Process {process.id} failed: {e}")
#         finally:
#             # Cleanup
#             if process.id in self.processes:
#                 del self.processes[process.id]
#             if process.id in self.process_threads:
#                 del self.process_threads[process.id]

#     def send_heartbeat(self):
#         """Sende Heartbeat mit aktuellem Status"""
#         msg = AgentHeartbeatMessage(self.id, len(self.processes))
#         self.connector.send(f"coordinator_{self.coordinator_id}", msg.to_json())

#     def report_process_complete(self, process_id: int, final_value: int):
#         """Melde Prozess-Abschluss dem Coordinator"""
#         msg = ProcessCompleteMessage(self.id, process_id, final_value)
#         self.connector.send(f"coordinator_{self.coordinator_id}", msg.to_json())
#         logger.info(f"Agent {self.id}: Reported process {process_id} complete with result {final_value}")

#     def cleanup(self):
#         """Cleanup bei Shutdown"""
#         try:
#             self.is_running = False
            
#             # Stoppe alle Prozesse
#             for process in self.processes.values():
#                 process.stop()
            
#             # Warte auf Threads
#             for thread in self.process_threads.values():
#                 thread.join(timeout=2)
            
#             # Cleanup Connector
#             if self.connector:
#                 self.connector.cleanup()
            
#             logger.info(f"Agent {self.id}: Cleanup complete")
#         except Exception as e:
#             logger.error(f"Agent {self.id} cleanup error: {e}")


# def main():
#     import sys
    
#     if len(sys.argv) < 2:
#         print("Usage: agent.py <agent_id> [coordinator_id] [capacity] [host]")
#         print("Example: agent.py 1 0 10 localhost")
#         sys.exit(1)
    
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#     )
    
#     agent_id = int(sys.argv[1])
#     coordinator_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
#     capacity = int(sys.argv[3]) if len(sys.argv) > 3 else 10
#     host = sys.argv[4] if len(sys.argv) > 4 else "localhost"
    
#     agent = Agent(agent_id, coordinator_id, capacity, host)
    
#     try:
#         agent.start()
#     except KeyboardInterrupt:
#         logger.info(f"Agent {agent_id}: Shutdown requested")
#         agent.cleanup()


# if __name__ == "__main__":
#     main()
