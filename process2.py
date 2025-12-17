import time
import datetime
import logging
import threading
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
        self.lock = threading.Lock()

    def start(self, initial_wait: float = 2, convergence_time: float = 20):
        """
        Starte den GGT-Prozess.
        
        Args:
            initial_wait: Wartezeit bevor Wert gebroadcasted wird (Sekunden)
            convergence_time: Maximale Laufzeit (Sekunden)
        """
        try:
            logger.info(f"Process {self.id}: Starting with M={self.algorithm.M}")
            
            # WICHTIG: Registriere diese Prozess-Queue beim Connector
            self.connector.connect_process_queue(self.id)
            logger.info(f"Process {self.id}: Queue registered")
            
            # Warte, bis andere Prozesse gestartet sind
            time.sleep(initial_wait)
            
            # Initialer Broadcast
            self.broadcast_value()
            logger.info(f"Process {self.id}: Initial broadcast done (M={self.algorithm.M})")
            
            start = datetime.datetime.now()
            
            # Hauptschleife
            iteration = 0
            while self.is_running:
                iteration += 1
                
                # Versuche, Nachrichten zu empfangen
                raw_msg = self.connector.receive()
                
                if raw_msg:
                    try:
                        msg = Message.from_json(raw_msg)
                        
                        if isinstance(msg, GGTValueMessage):
                            old_m = self.algorithm.M
                            changed = self.algorithm.update_value(msg.value)
                            
                            if changed:
                                logger.info(f"Process {self.id}: M updated {old_m} → {self.algorithm.M} (from value {msg.value})")
                                self.broadcast_value()
                            else:
                                logger.debug(f"Process {self.id}: Received {msg.value}, M unchanged at {self.algorithm.M}")
                    
                    except Exception as e:
                        logger.error(f"Process {self.id}: Parse error: {e}")
                
                # Prüfe Timeout
                elapsed = (datetime.datetime.now() - start).total_seconds()
                if elapsed > convergence_time:
                    logger.info(f"Process {self.id}: Convergence timeout ({elapsed:.1f}s > {convergence_time}s)")
                    break
                
                # Debug every 20 iterations
                if iteration % 20 == 0:
                    logger.debug(f"Process {self.id}: Still running, M={self.algorithm.M}, elapsed={elapsed:.1f}s")
                
                time.sleep(0.01)
            
            logger.info(f"Process {self.id}: Finished with M={self.algorithm.M}")
        
        except Exception as e:
            logger.error(f"Process {self.id}: Error in start: {e}")
            import traceback
            traceback.print_exc()

    def broadcast_value(self):
        """Sende aktuellen M-Wert an Vorgänger und Nachfolger"""
        msg = GGTValueMessage(self.id, self.algorithm.M)
        msg_json = msg.to_json()
        
        # Sende an Vorgänger
        target_pred = f"process_{self.predecessor}"
        self.connector.send(target_pred, msg_json)
        logger.debug(f"Process {self.id}: Sent M={self.algorithm.M} to {target_pred}")
        
        # Sende an Nachfolger
        target_succ = f"process_{self.successor}"
        self.connector.send(target_succ, msg_json)
        logger.debug(f"Process {self.id}: Sent M={self.algorithm.M} to {target_succ}")

    def get_result(self) -> int:
        """Gib das finale Ergebnis zurück"""
        return self.algorithm.M

    def stop(self):
        """Stoppe den Prozess"""
        self.is_running = False
        logger.info(f"Process {self.id}: Stop requested")
