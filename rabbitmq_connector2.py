import rabbitpy
import logging
from typing import Optional
from queue import Queue
from threading import Thread
import json

logger = logging.getLogger(__name__)


class RabbitMQConnector:
    """Vereinheitlichter RabbitMQ-Connector für alle Komponenten"""
    
    def __init__(self, host: str, component_id: int, component_type: str):
        """
        Args:
            host: RabbitMQ Host
            component_id: eindeutige ID der Komponente
            component_type: 'coordinator', 'agent', oder 'process'
        """
        self.host = host
        self.component_id = component_id
        self.component_type = component_type
        
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        self.queue_name = f"{component_type}_{component_id}"
        
        self.message_queue = Queue()
        self.receiving = False
        self.receive_thread = None

    def connect(self):
        """Verbindung zu RabbitMQ aufbauen"""
        try:
            self.connection = rabbitpy.Connection(f"amqp://guest:guest@{self.host}:5672/%2F")
            self.channel = self.connection.channel()
            
            # Exchange für alle Nachrichten
            self.exchange = rabbitpy.Exchange(self.channel, "ggt_exchange", "direct")
            self.exchange.declare()
            
            # Queue für diese Komponente
            self.queue = rabbitpy.Queue(self.channel, self.queue_name)
            self.queue.declare()
            
            # Binding
            self.queue.bind(self.exchange, self.queue_name)
            
            logger.info(f"RabbitMQ connected: {self.component_type}_{self.component_id}")
            
            # Starte Receive-Thread
            self.start_receiving()
            
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            raise

    def connect_process_queue(self, process_id: int):
        """
        Erstelle zusätzliche Queue für einen GGT-Prozess.
        Wird vom Prozess aufgerufen um seine eigene Queue zu registrieren.
        """
        try:
            queue_name = f"process_{process_id}"
            process_queue = rabbitpy.Queue(self.channel, queue_name)
            process_queue.declare()
            process_queue.bind(self.exchange, queue_name)
            logger.info(f"Process queue created: {queue_name}")
        except Exception as e:
            logger.error(f"Failed to create process queue {process_id}: {e}")
            raise

    def start_receiving(self):
        """Starte Background-Thread für Message-Empfang"""
        self.receiving = True
        self.receive_thread = Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()

    def _receive_loop(self):
        """Background-Loop zum Empfangen von Nachrichten"""
        try:
            for message in self.queue.consume():
                if message:
                    try:
                        data = message.body.decode("utf-8")
                        self.message_queue.put(data)
                        message.ack()
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        message.nack()
                
                if not self.receiving:
                    break
        except Exception as e:
            logger.error(f"Receive loop error: {e}")

    def send(self, target_queue: str, message_json: str):
        """Sende eine Nachricht"""
        try:
            msg = rabbitpy.Message(self.channel, message_json)
            msg.properties["content_type"] = "application/json"
            msg.publish(self.exchange, target_queue)
            logger.debug(f"Message sent to {target_queue}")
        except Exception as e:
            logger.error(f"Send error to {target_queue}: {e}")

    def receive(self) -> Optional[str]:
        """Versuche, eine Nachricht zu empfangen (non-blocking)"""
        try:
            return self.message_queue.get_nowait()
        except:
            return None

    def cleanup(self):
        """Cleanup bei Shutdown"""
        try:
            self.receiving = False
            if self.receive_thread:
                self.receive_thread.join(timeout=2)
            
            if self.queue:
                self.queue.delete()
            if self.exchange:
                self.exchange.delete()
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
            
            logger.info(f"RabbitMQ cleanup: {self.component_type}_{self.component_id}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
