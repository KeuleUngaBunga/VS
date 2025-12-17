import time
import datetime
import logging
from algorithm import GGTAlgorithm
from message import GGTValueMessage, Message, ProcessCompleteMessage

logger = logging.getLogger(__name__)


class GGTProcess:
    """Ein einzelner GGT-Prozess, der auf einem Agent läuft"""
    
    def __init__(self, process_id: int, initial_value: int, 
                 predecessor_id: int, successor_id: int, 
                 connector, agent_id: int):
        self.id = process_id
        self.predecessor = predecessor_id
        self.successor = successor_id
        self.algorithm = GGTAlgorithm(initial_value)
        self.connector = connector
        self.agent_id = agent_id
        self.is_running = True

    def start(self, initial_wait: float = 5, convergence_time: float = 30):
        """
        Starte den GGT-Prozess.
        
        Args:
            initial_wait: Wartezeit bevor Wert gebroadcasted wird (Sekunden)
            convergence_time: Maximale Laufzeit (Sekunden)
        """
        logger.info(f"Process {self.id}: Starting with M={self.algorithm.M}")
        
        # Warte, bis andere Prozesse gestartet sind
        time.sleep(initial_wait)
        
        # Initialer Broadcast
        self.broadcast_value()
        
        start = datetime.datetime.now()
        
        # Hauptschleife
        while self.is_running:
            # Versuche, Nachrichten zu empfangen
            raw_msg = self.connector.receive()
            
            if raw_msg:
                try:
                    msg = Message.from_json(raw_msg)
                    
                    if isinstance(msg, GGTValueMessage):
                        changed = self.algorithm.update_value(msg.value)
                        if changed:
                            logger.info(f"Process {self.id}: M updated to {self.algorithm.M}")
                            self.broadcast_value()
                
                except Exception as e:
                    logger.error(f"Process {self.id}: Parse error: {e}")
            
            # Prüfe Timeout
            elapsed = (datetime.datetime.now() - start).total_seconds()
            if elapsed > convergence_time:
                logger.info(f"Process {self.id}: Convergence timeout")
                break
            
            time.sleep(0.01)

    def broadcast_value(self):
        """Sende aktuellen M-Wert an Vorgänger und Nachfolger"""
        msg = GGTValueMessage(self.id, self.algorithm.M)
        msg_json = msg.to_json()
        
        # Sende an Vorgänger
        self.connector.send(f"process_{self.predecessor}", msg_json)
        
        # Sende an Nachfolger
        self.connector.send(f"process_{self.successor}", msg_json)
        
        logger.debug(f"Process {self.id}: Broadcasted M={self.algorithm.M}")

    def get_result(self) -> int:
        """Gib das finale Ergebnis zurück"""
        return self.algorithm.M

    def stop(self):
        """Stoppe den Prozess"""
        self.is_running = False
