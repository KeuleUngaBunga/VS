from queue import Queue, Empty
import time

from algorithm import GGTAlgorithm

class GGTProcess:

    def __init__(
        self,
        process_id: int,
        initial_value: int,
        inbox: Queue,
        outbox: Queue
    ):
        self.id = process_id
        self.algorithm = GGTAlgorithm(initial_value)
        self.inbox = inbox      # Nachrichten VON Agent
        self.outbox = outbox    # Nachrichten AN Agent
        self.is_running = True

    def start(self, convergence_time: float = 60.0):
        start_time = time.time()

        # initial broadcast
        self.outbox.put((self.id, self.algorithm.M))

        while self.is_running:
            try:
                sender_id, value = self.inbox.get(timeout=0.5)
                changed = self.algorithm.update_value(value)

                if changed:
                    self.outbox.put((self.id, self.algorithm.M))

            except Empty:
                pass

            if time.time() - start_time > convergence_time:
                break


# import time
# import datetime
# import logging

# from algorithm import GGTAlgorithm
# # from message_parser import MessageParser
# from message import GGTValueMessage, Message

# logger = logging.getLogger(__name__)


# class GGTProcess:
#     """
#     Ein einzelner GGT-Prozess.
#     Nutzt den gemeinsamen RabbitMQConnector des Agents.
#     """

#     def __init__(
#         self,
#         process_id: int,
#         initial_value: int,
#         predecessor_id: int,
#         successor_id: int,
#         connector,
#         agent_id: int
#     ):
#         self.id = process_id
#         self.predecessor = predecessor_id
#         self.successor = successor_id

#         self.algorithm = GGTAlgorithm(initial_value)
#         self.connector = connector
#         self.agent_id = agent_id

#         self.is_running = True

#     # ------------------------------------------------------------

#     def start(self, initial_wait: float = 5.0, convergence_time: float = 60.0):
#         """
#         Starte den GGT-Prozess.
#         Connector ist bereits verbunden!
#         """

#         logger.info(
#             f"Process {self.id}: Waiting {initial_wait}s before start"
#         )
#         time.sleep(initial_wait)

#         logger.info(
#             f"Process {self.id}: Starting with M={self.algorithm.M}"
#         )
#         self.broadcast_value()

#         start_time = datetime.datetime.now()

#         while self.is_running:
#             # raw_msg = self.connector.receive()

#             if raw_msg:
#                 msg = Message.from_json(raw_msg)

#                 if msg:
#                     changed = self.algorithm.update_value(msg.value)

#                     if changed:
#                         logger.info(
#                             f"Process {self.id}: M updated to {self.algorithm.M}"
#                         )
#                         self.broadcast_value()

#             if (
#                 datetime.datetime.now() - start_time
#             ).total_seconds() > convergence_time:
#                 logger.info(
#                     f"Process {self.id}: Convergence timeout reached"
#                 )
#                 break

#             time.sleep(0.01)

#         logger.info(
#             f"Process {self.id}: Finished with M={self.algorithm.M}"
#         )

#     # ------------------------------------------------------------

#     from message import GGTValueMessage

#     # def broadcast_value(self):
#     #     m = self.algorithm.M
#     #     msg = GGTValueMessage(sender_id=self.id, value=m)

#     #     self.connector.send(
#     #         f"process_{self.predecessor}",
#     #         msg.to_json()
#     #     )
#     #     self.connector.send(
#     #         f"process_{self.successor}",
#     #         msg.to_json()
#     #     )


#     # ------------------------------------------------------------

#     def get_result(self) -> int:
#         return self.algorithm.M

#     # ------------------------------------------------------------

#     def stop(self):
#         self.is_running = False


# import time
# import datetime
# import logging
# from algorithm import GGTAlgorithm
# from message_parser import MessageParser
# from message import GGTMessage

# logger = logging.getLogger(__name__)

# class GGTProcess:
#     def __init__(self, process_id, initial_value, predecessor_id, successor_id, connector, bus):
#         self.id = process_id
#         self.predecessor = predecessor_id
#         self.successor = successor_id
#         self.algorithm = GGTAlgorithm(initial_value)
#         self.bus = bus
#         self.connector = connector
#         self.is_running = True

#     def start(self, initial_wait=15, convergence_time=60):
#         self.connector.connect()

#         logger.info(f"Process {self.id}: Waiting {initial_wait}s for others...")
#         time.sleep(initial_wait)

#         logger.info(f"Process {self.id}: Starting with M={self.algorithm.M}")
#         self.broadcast_value()

#         start = datetime.datetime.now()

#         while self.is_running:
#             incoming_raw = self.bus.receive()
#             if incoming_raw:
#                 msg = MessageParser.parse(incoming_raw)
#                 if msg:
#                     changed = self.algorithm.update_value(msg.value)
#                     if changed:
#                         logger.info(f"Process {self.id}: M updated to {self.algorithm.M}")
#                         self.broadcast_value()

#             if (datetime.datetime.now() - start).total_seconds() > convergence_time:
#                 break

#             time.sleep(0.01)

#         logger.info(f"Process {self.id}: Finished with M={self.algorithm.M}")
#         self.connector.cleanup()

#     def broadcast_value(self):
#         m = self.algorithm.M
#         msg = GGTMessage(sender_id=self.id, value=m)
#         self.bus.send(self.predecessor, msg)
#         self.bus.send(self.successor, msg)

# # import time
# # import datetime
# # import logging
# # import threading
# # from algorithm import GGTAlgorithm
# # from message import GGTValueMessage, Message, ProcessCompleteMessage

# # logger = logging.getLogger(__name__)


# # class GGTProcess:
# #     """Ein einzelner GGT-Prozess, der auf einem Agent läuft"""
    
# #     def __init__(self, process_id: int, initial_value: int, 
# #                  predecessor_id: int, successor_id: int, 
# #                  connector, agent_id: int):
# #         self.id = process_id
# #         self.predecessor = predecessor_id
# #         self.successor = successor_id
# #         self.algorithm = GGTAlgorithm(initial_value)
# #         self.connector = connector
# #         self.agent_id = agent_id
# #         self.is_running = True
# #         self.lock = threading.Lock()

# #     def start(self, initial_wait: float = 2, convergence_time: float = 20):
# #         """
# #         Starte den GGT-Prozess.
        
# #         Args:
# #             initial_wait: Wartezeit bevor Wert gebroadcasted wird (Sekunden)
# #             convergence_time: Maximale Laufzeit (Sekunden)
# #         """
# #         try:
# #             logger.info(f"Process {self.id}: Starting with M={self.algorithm.M}")
            
# #             # WICHTIG: Registriere diese Prozess-Queue beim Connector
# #             # Dies erstellt SEPARATE Receive-Thread und Message-Queue für diesen Prozess
# #             self.connector.connect_process_queue(self.id)
# #             logger.info(f"Process {self.id}: Queue registered with separate receive thread")
            
# #             # Warte, bis andere Prozesse gestartet sind
# #             time.sleep(initial_wait)
            
# #             # Initialer Broadcast
# #             self.broadcast_value()
# #             logger.info(f"Process {self.id}: Initial broadcast done (M={self.algorithm.M})")
            
# #             start = datetime.datetime.now()
            
# #             # Hauptschleife
# #             iteration = 0
# #             updates = 0
# #             while self.is_running:
# #                 iteration += 1
                
# #                 # Versuche, Nachrichten zu empfangen VOM PROZESS (nicht vom Agent!)
# #                 # WICHTIG: Benutze receive_process() statt receive()!
# #                 raw_msg = self.connector.receive_process(self.id)
                
# #                 if raw_msg:
# #                     try:
# #                         msg = Message.from_json(raw_msg)
                        
# #                         if isinstance(msg, GGTValueMessage):
# #                             old_m = self.algorithm.M
# #                             changed = self.algorithm.update_value(msg.value)
                            
# #                             if changed:
# #                                 updates += 1
# #                                 logger.info(f"Process {self.id}: M updated {old_m} → {self.algorithm.M} (from value {msg.value}) [update #{updates}]")
# #                                 self.broadcast_value()
# #                             else:
# #                                 logger.debug(f"Process {self.id}: Received {msg.value}, M unchanged at {self.algorithm.M}")
                    
# #                     except Exception as e:
# #                         logger.error(f"Process {self.id}: Parse error: {e}")
                
# #                 # Prüfe Timeout
# #                 elapsed = (datetime.datetime.now() - start).total_seconds()
# #                 if elapsed > convergence_time:
# #                     logger.info(f"Process {self.id}: Convergence timeout ({elapsed:.1f}s > {convergence_time}s, {updates} updates)")
# #                     break
                
# #                 # Debug every 50 iterations
# #                 if iteration % 50 == 0:
# #                     logger.debug(f"Process {self.id}: Still running, M={self.algorithm.M}, elapsed={elapsed:.1f}s, updates={updates}")
                
# #                 time.sleep(0.01)
            
# #             logger.info(f"Process {self.id}: Finished with M={self.algorithm.M} (total updates: {updates})")
        
# #         except Exception as e:
# #             logger.error(f"Process {self.id}: Error in start: {e}")
# #             import traceback
# #             traceback.print_exc()

# #     def broadcast_value(self):
# #         """Sende aktuellen M-Wert an Vorgänger und Nachfolger"""
# #         msg = GGTValueMessage(self.id, self.algorithm.M)
# #         msg_json = msg.to_json()
        
# #         # Sende an Vorgänger
# #         target_pred = f"process_{self.predecessor}"
# #         self.connector.send(target_pred, msg_json)
# #         logger.info(f"Process {self.id}: Sent M={self.algorithm.M} to {target_pred}")
        
# #         # Sende an Nachfolger
# #         target_succ = f"process_{self.successor}"
# #         self.connector.send(target_succ, msg_json)
# #         logger.info(f"Process {self.id}: Sent M={self.algorithm.M} to {target_succ}")

#     def get_result(self) -> int:
#         """Gib das finale Ergebnis zurück"""
#         return self.algorithm.M

# #     def stop(self):
# #         """Stoppe den Prozess"""
# #         self.is_running = False
# #         logger.info(f"Process {self.id}: Stop requested")
