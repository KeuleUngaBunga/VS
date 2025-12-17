import logging
import time
import threading
from typing import Dict, List, Tuple
from rabbitmq_connector import RabbitMQConnector
from message import (
    CoordinatorReadyMessage, AgentRegisterMessage, AgentHeartbeatMessage,
    StartProcessMessage, ProcessCompleteMessage, Message
)

logger = logging.getLogger(__name__)


class Coordinator:
    """
    Koordinator der GGT-Berechnung.
    
    - Registriert verfügbare Agents
    - Erstellt einen Ring von Prozessen
    - Verteilt Prozesse gleichmäßig auf Agents
    - Sammelt Ergebnisse
    """
    
    def __init__(self, coordinator_id: int = 0, host: str = "localhost"):
        """
        Args:
            coordinator_id: Eindeutige Coordinator-ID
            host: RabbitMQ Host
        """
        self.id = coordinator_id
        self.host = host
        
        self.connector = None
        self.agents: Dict[int, Dict] = {}  # agent_id -> {capacity, active_processes}
        self.process_results: Dict[int, int] = {}  # process_id -> final_value
        
        self.is_running = False
        self.registration_phase = False
        self.computation_phase = False

    def start(self):
        """Starte den Coordinator"""
        try:
            # Verbinde zu RabbitMQ
            self.connector = RabbitMQConnector(self.host, self.id, "coordinator")
            self.connector.connect()
            
            self.is_running = True
            logger.info(f"Coordinator {self.id} started")
            
            # Kündige Bereitschaft an
            self.announce_ready()
            
            # Starte Message-Loop
            self.message_loop()
            
        except Exception as e:
            logger.error(f"Coordinator {self.id} startup failed: {e}")
            self.cleanup()
            raise

    def announce_ready(self):
        """Künde an, dass dieser Coordinator bereit ist"""
        msg = CoordinatorReadyMessage(self.id)
        # Broadcast an alle Agents (sie werden automatisch binten)
        logger.info(f"Coordinator {self.id}: Announcement ready")

    def message_loop(self):
        """Hauptschleife für Message-Verarbeitung"""
        while self.is_running:
            try:
                raw_msg = self.connector.receive()
                
                if raw_msg:
                    msg = Message.from_json(raw_msg)
                    
                    if isinstance(msg, AgentRegisterMessage):
                        self.handle_agent_register(msg)
                    elif isinstance(msg, ProcessCompleteMessage):
                        self.handle_process_complete(msg)
                    elif isinstance(msg, AgentHeartbeatMessage):
                        self.handle_agent_heartbeat(msg)
                    else:
                        logger.warning(f"Coordinator: Unknown message type: {type(msg)}")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Coordinator message loop error: {e}")

    def handle_agent_register(self, msg: AgentRegisterMessage):
        """Verarbeite Agenten-Registrierung"""
        agent_id = msg.sender_id
        capacity = msg.capacity
        
        if agent_id not in self.agents:
            self.agents[agent_id] = {
                "capacity": capacity,
                "active_processes": 0
            }
            logger.info(f"Coordinator: Agent {agent_id} registered (capacity={capacity})")
        else:
            logger.warning(f"Coordinator: Agent {agent_id} already registered")

    def handle_agent_heartbeat(self, msg: AgentHeartbeatMessage):
        """Verarbeite Agent-Heartbeat"""
        agent_id = msg.sender_id
        active_processes = msg.active_processes
        
        if agent_id in self.agents:
            self.agents[agent_id]["active_processes"] = active_processes
            logger.debug(f"Coordinator: Agent {agent_id} heartbeat ({active_processes} active)")

    def handle_process_complete(self, msg: ProcessCompleteMessage):
        """Verarbeite Prozess-Abschluss"""
        process_id = msg.process_id
        final_value = msg.final_value
        agent_id = msg.sender_id
        
        self.process_results[process_id] = final_value
        logger.info(f"Coordinator: Process {process_id} complete with result {final_value} (Agent {agent_id})")

    def start_ggt_computation(self, values: List[int], registration_timeout: float = 10) -> Dict[int, int]:
        """
        Starte GGT-Berechnung für die gegebenen Werte.
        
        Args:
            values: Liste der Werte für den GGT-Ring
            registration_timeout: Zeit zum Warten auf Agent-Registrierungen (Sekunden)
        
        Returns:
            Dict mit process_id -> final_value
        """
        n = len(values)
        
        if n == 0:
            logger.error("Coordinator: No values provided")
            return {}
        
        logger.info(f"Coordinator: Starting GGT computation for {n} values: {values}")
        
        # Warte auf Agent-Registrierungen
        logger.info(f"Coordinator: Waiting {registration_timeout}s for agent registrations...")
        time.sleep(registration_timeout)
        
        if not self.agents:
            logger.error("Coordinator: No agents registered!")
            return {}
        
        logger.info(f"Coordinator: {len(self.agents)} agents registered")
        for agent_id, agent_info in self.agents.items():
            logger.info(f"  - Agent {agent_id}: capacity={agent_info['capacity']}")
        
        # Erstelle Ring-Topologie
        # Prozess i hat als predecessor (i-1) % n und successor (i+1) % n
        processes_to_create = []
        for i in range(n):
            process_id = i
            initial_value = values[i]
            predecessor_id = (i - 1) % n
            successor_id = (i + 1) % n
            
            processes_to_create.append({
                "process_id": process_id,
                "initial_value": initial_value,
                "predecessor_id": predecessor_id,
                "successor_id": successor_id
            })
        
        # Verteile Prozesse gleichmäßig auf Agents (Load Balancing)
        agent_ids = list(self.agents.keys())
        agent_assignments = {aid: [] for aid in agent_ids}
        
        for idx, proc_spec in enumerate(processes_to_create):
            # Round-Robin Verteilung
            assigned_agent = agent_ids[idx % len(agent_ids)]
            agent_assignments[assigned_agent].append(proc_spec)
        
        # Sende START_PROCESS Befehle an Agents
        logger.info("Coordinator: Distributing processes to agents...")
        for agent_id, processes in agent_assignments.items():
            for proc_spec in processes:
                msg = StartProcessMessage(
                    self.id,
                    proc_spec["process_id"],
                    proc_spec["initial_value"],
                    proc_spec["predecessor_id"],
                    proc_spec["successor_id"]
                )
                self.connector.send(f"agent_{agent_id}", msg.to_json())
                logger.info(f"Coordinator: Process {proc_spec['process_id']} -> Agent {agent_id}")
                time.sleep(0.05)  # Kleine Verzögerung zwischen Befehlen
        
        # Warte auf Abschluss aller Prozesse
        logger.info("Coordinator: Waiting for process completions...")
        max_wait = 120  # Maximale Wartezeit (Sekunden)
        start_time = time.time()
        
        while len(self.process_results) < n:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                logger.error(f"Coordinator: Timeout! Only {len(self.process_results)}/{n} processes completed")
                break
            
            time.sleep(0.5)
        
        # Zeige Ergebnisse
        logger.info("=" * 60)
        logger.info("COORDINATOR: GGT COMPUTATION RESULTS")
        logger.info("=" * 60)
        for i in range(n):
            if i in self.process_results:
                logger.info(f"Process {i} (initial value {values[i]}): final M = {self.process_results[i]}")
            else:
                logger.warning(f"Process {i}: NO RESULT")
        logger.info("=" * 60)
        
        return self.process_results

    def cleanup(self):
        """Cleanup bei Shutdown"""
        try:
            self.is_running = False
            
            if self.connector:
                self.connector.cleanup()
            
            logger.info(f"Coordinator {self.id}: Cleanup complete")
        except Exception as e:
            logger.error(f"Coordinator {self.id} cleanup error: {e}")


def interactive_mode(coordinator: Coordinator):
    """Interaktive Eingabe für GGT-Parameter"""
    print("\n" + "=" * 60)
    print("GGT DISTRIBUTED SYSTEM - COORDINATOR")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Start GGT computation")
        print("2. Show registered agents")
        print("3. Show process results")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            values_str = input("Enter values separated by commas (e.g., 12,18,24): ").strip()
            try:
                values = [int(v.strip()) for v in values_str.split(",")]
                if len(values) < 2:
                    print("ERROR: Need at least 2 values for a ring")
                    continue
                
                print(f"\nStarting GGT computation for {len(values)} values...")
                results = coordinator.start_ggt_computation(values, registration_timeout=10)
                
                if results:
                    print(f"\n✓ Computation complete! {len(results)}/{len(values)} processes finished")
                else:
                    print("\n✗ Computation failed or timed out")
            
            except ValueError:
                print("ERROR: Invalid input. Please enter comma-separated integers.")
        
        elif choice == "2":
            if coordinator.agents:
                print("\nRegistered Agents:")
                for agent_id, info in coordinator.agents.items():
                    print(f"  Agent {agent_id}: capacity={info['capacity']}, active={info['active_processes']}")
            else:
                print("\nNo agents registered")
        
        elif choice == "3":
            if coordinator.process_results:
                print("\nProcess Results:")
                for proc_id, result in sorted(coordinator.process_results.items()):
                    print(f"  Process {proc_id}: M = {result}")
            else:
                print("\nNo process results yet")
        
        elif choice == "4":
            print("\nShutting down...")
            coordinator.cleanup()
            break
        
        else:
            print("Invalid choice")


def main():
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    coordinator_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
    
    coordinator = Coordinator(coordinator_id, host)
    
    try:
        # Starte Coordinator in eigenem Thread
        coordinator_thread = threading.Thread(target=coordinator.start, daemon=True)
        coordinator_thread.start()
        
        # Warte kurz bis Coordinator bereit ist
        time.sleep(1)
        
        # Starte interaktiven Modus
        interactive_mode(coordinator)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        coordinator.cleanup()


if __name__ == "__main__":
    main()
