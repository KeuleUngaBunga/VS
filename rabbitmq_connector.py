import rabbitpy
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RabbitMQConnector:
    """
    Einheitlicher RabbitMQ-Connector für:
    - coordinator
    - agent
    - process
    """

    def __init__(self, host: str, role: str, component_id: int):
        """
        Args:
            host: RabbitMQ Host
            role: 'coordinator' | 'agent' | 'process'
            component_id: eindeutige ID
        """
        self.host = host
        self.role = role
        self.component_id = component_id

        self.queue_name = f"{role}_{component_id}"

        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None

    # ------------------------------------------------------------------

    def connect(self):
        """Verbindung aufbauen und eigene Queue registrieren"""
        self.connection = rabbitpy.Connection(
            f"amqp://guest:guest@{self.host}:5672/%2F"
        )
        self.channel = self.connection.channel()

        self.exchange = rabbitpy.Exchange(
            self.channel, "ggt_exchange", "direct"
        )
        self.exchange.declare()

        self.queue = rabbitpy.Queue(self.channel, self.queue_name)
        self.queue.declare()
        self.queue.bind(self.exchange, self.queue_name)

        logger.info(f"RabbitMQ ready: {self.queue_name}")

    # ------------------------------------------------------------------

    def send(self, target: str, payload: str):
        """
        Sende Nachricht an beliebige Komponente

        target Beispiele:
            - 'coordinator_1'
            - 'agent_2'
            - 'process_7'
        """
        msg = rabbitpy.Message(self.channel, payload)
        msg.properties["content_type"] = "application/json"
        msg.publish(self.exchange, target)

    # ------------------------------------------------------------------

    def receive(self, timeout: float = 0.1) -> Optional[str]:
        """
        Empfange genau eine Nachricht (non-blocking)
        """
        for message in self.queue.consume(prefetch=1):
            if message:
                body = message.body.decode("utf-8")
                message.ack()
                return body
        return None

    # ------------------------------------------------------------------

    def cleanup(self):
        """Sauberer Shutdown"""
        try:
            if self.queue:
                self.queue.delete()
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# import rabbitpy
# import logging

# logger = logging.getLogger(__name__)

# class RabbitMQConnector:
#     def __init__(self, host: str, process_id: int):
#         self.host = host
#         self.process_id = process_id
#         self.connection = None
#         self.channel = None
#         self.exchange = None
#         self.queue = None

#     def connect(self):
#         self.connection = rabbitpy.Connection(f"amqp://guest:guest@{self.host}:5672/%2F")
#         self.channel = self.connection.channel()

#         self.exchange = rabbitpy.Exchange(self.channel, "ggt_exchange", "direct")
#         self.exchange.declare()

#         queue_name = f"ggt_process_{self.process_id}"
#         self.queue = rabbitpy.Queue(self.channel, queue_name)
#         self.queue.declare()

#         self.queue.bind(self.exchange, f"process_{self.process_id}")
#         logger.info(f"RabbitMQ ready for process {self.process_id}")

#     def cleanup(self):
#         try:
#             if self.queue:
#                 self.queue.delete()
#             if self.exchange:
#                 self.exchange.delete()
#             if self.channel:
#                 self.channel.close()
#             if self.connection:
#                 self.connection.close()
#         except Exception as e:
#             logger.error(f"Cleanup failed: {e}")
            
# # import rabbitpy
# # import logging
# # from typing import Optional, Dict
# # from queue import Queue
# # from threading import Thread
# # import json

# # logger = logging.getLogger(__name__)


# # class RabbitMQConnector:
# #     """Vereinheitlichter RabbitMQ-Connector für alle Komponenten"""
    
# #     def __init__(self, host: str, component_id: int, component_type: str):
# #         """
# #         Args:
# #             host: RabbitMQ Host
# #             component_id: eindeutige ID der Komponente
# #             component_type: 'coordinator', 'agent', oder 'process'
# #         """
# #         self.host = host
# #         self.component_id = component_id
# #         self.component_type = component_type
        
# #         self.connection = None
# #         self.channel = None
# #         self.exchange = None
# #         self.queue = None
# #         self.queue_name = f"{component_type}_{component_id}"
        
# #         # WICHTIG: Separate Message-Queues für jeden Prozess!
# #         self.message_queue = Queue()
# #         self.process_queues: Dict[int, Queue] = {}  # process_id -> Queue
        
# #         self.receiving = False
# #         self.receive_thread = None
# #         self.process_receive_threads: Dict[int, Thread] = {}

# #     def connect(self):
# #         """Verbindung zu RabbitMQ aufbauen"""
# #         try:
# #             self.connection = rabbitpy.Connection(f"amqp://guest:guest@{self.host}:5672/%2F")
# #             self.channel = self.connection.channel()
            
# #             # Exchange für alle Nachrichten
# #             self.exchange = rabbitpy.Exchange(self.channel, "ggt_exchange", "direct")
# #             self.exchange.declare()
            
# #             # Queue für diese Komponente (Agent oder Coordinator)
# #             self.queue = rabbitpy.Queue(self.channel, self.queue_name)
# #             self.queue.declare()
            
# #             # Binding
# #             self.queue.bind(self.exchange, self.queue_name)
            
# #             logger.info(f"RabbitMQ connected: {self.component_type}_{self.component_id}")
            
# #             # Starte Receive-Thread für diese Komponente
# #             self.start_receiving()
            
# #         except Exception as e:
# #             logger.error(f"RabbitMQ connection failed: {e}")
# #             raise

# #     def connect_process_queue(self, process_id: int):
# #         """
# #         Erstelle SEPARATE Queue und Receive-Thread für einen GGT-Prozess.
# #         WICHTIG: Jeder Prozess braucht seinen eigenen Receive-Thread!
# #         """
# #         try:
# #             queue_name = f"process_{process_id}"
# #             process_queue_obj = rabbitpy.Queue(self.channel, queue_name)
# #             process_queue_obj.declare()
# #             process_queue_obj.bind(self.exchange, queue_name)
            
# #             # Erstelle separate Python-Queue für diesen Prozess
# #             self.process_queues[process_id] = Queue()
            
# #             # Starte separaten Receive-Thread für diesen Prozess
# #             thread = Thread(
# #                 target=self._receive_loop_process,
# #                 args=(process_id, process_queue_obj),
# #                 daemon=True
# #             )
# #             thread.start()
# #             self.process_receive_threads[process_id] = thread
            
# #             logger.info(f"Process queue created and receiving thread started: {queue_name}")
# #         except Exception as e:
# #             logger.error(f"Failed to create process queue {process_id}: {e}")
# #             raise

# #     def start_receiving(self):
# #         """Starte Background-Thread für Message-Empfang (Agent/Coordinator Queue)"""
# #         self.receiving = True
# #         self.receive_thread = Thread(target=self._receive_loop, daemon=True)
# #         self.receive_thread.start()

# #     def _receive_loop(self):
# #         """Background-Loop zum Empfangen von Nachrichten in Agent/Coordinator Queue"""
# #         try:
# #             for message in self.queue.consume():
# #                 if message:
# #                     try:
# #                         data = message.body.decode("utf-8")
# #                         self.message_queue.put(data)
# #                         message.ack()
# #                     except Exception as e:
# #                         logger.error(f"Error processing message: {e}")
# #                         message.nack()
                
# #                 if not self.receiving:
# #                     break
# #         except Exception as e:
# #             logger.error(f"Receive loop error: {e}")

# #     def _receive_loop_process(self, process_id: int, queue_obj):
# #         """Background-Loop zum Empfangen von Nachrichten in Process Queue"""
# #         try:
# #             logger.debug(f"Process {process_id} receive loop started")
# #             for message in queue_obj.consume():
# #                 if message:
# #                     try:
# #                         data = message.body.decode("utf-8")
# #                         if process_id in self.process_queues:
# #                             self.process_queues[process_id].put(data)
# #                         message.ack()
# #                     except Exception as e:
# #                         logger.error(f"Error processing process {process_id} message: {e}")
# #                         message.nack()
# #         except Exception as e:
# #             logger.error(f"Process {process_id} receive loop error: {e}")

# #     def send(self, target_queue: str, message_json: str):
# #         """Sende eine Nachricht"""
# #         try:
# #             msg = rabbitpy.Message(self.channel, message_json)
# #             msg.properties["content_type"] = "application/json"
# #             msg.publish(self.exchange, target_queue)
# #             logger.debug(f"Message sent to {target_queue}")
# #         except Exception as e:
# #             logger.error(f"Send error to {target_queue}: {e}")

# #     def receive(self) -> Optional[str]:
# #         """Versuche, eine Nachricht zu empfangen von dieser Komponente (Agent/Coordinator)"""
# #         try:
# #             return self.message_queue.get_nowait()
# #         except:
# #             return None

# #     def receive_process(self, process_id: int) -> Optional[str]:
# #         """Versuche, eine Nachricht zu empfangen für einen spezifischen Prozess"""
# #         try:
# #             if process_id in self.process_queues:
# #                 return self.process_queues[process_id].get_nowait()
# #         except:
# #             pass
# #         return None

# #     def cleanup(self):
# #         """Cleanup bei Shutdown"""
# #         try:
# #             self.receiving = False
            
# #             if self.receive_thread:
# #                 self.receive_thread.join(timeout=2)
            
# #             for thread in self.process_receive_threads.values():
# #                 thread.join(timeout=2)
            
# #             if self.queue:
# #                 self.queue.delete()
# #             if self.exchange:
# #                 self.exchange.delete()
# #             if self.channel:
# #                 self.channel.close()
# #             if self.connection:
# #                 self.connection.close()
            
# #             logger.info(f"RabbitMQ cleanup: {self.component_type}_{self.component_id}")
# #         except Exception as e:
# #             logger.error(f"Cleanup failed: {e}")
