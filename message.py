import json
from enum import Enum
from typing import Optional


class MessageType(Enum):
    """Nachrichtentypen für das verteilte System"""
    GGT_VALUE = "ggt_value"  # GGT-Wert zwischen Prozessen
    AGENT_REGISTER = "agent_register"  # Agent registriert sich
    AGENT_HEARTBEAT = "agent_heartbeat"  # Agent Heartbeat
    START_PROCESS = "start_process"  # Coordinator startet einen Prozess
    PROCESS_COMPLETE = "process_complete"  # Prozess abgeschlossen
    COORDINATOR_READY = "coordinator_ready"  # Coordinator bereit


class Message:
    """Basis-Message-Klasse"""
    
    def __init__(self, msg_type: MessageType, sender_id: int, timestamp: Optional[float] = None):
        import time
        self.msg_type = msg_type.value
        self.sender_id = sender_id
        self.timestamp = timestamp or time.time()

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(text: str) -> 'Message':
        data = json.loads(text)
        msg_type = MessageType(data["msg_type"])
        
        if msg_type == MessageType.GGT_VALUE:
            return GGTValueMessage.from_dict(data)
        elif msg_type == MessageType.AGENT_REGISTER:
            return AgentRegisterMessage.from_dict(data)
        elif msg_type == MessageType.AGENT_HEARTBEAT:
            return AgentHeartbeatMessage.from_dict(data)
        elif msg_type == MessageType.START_PROCESS:
            return StartProcessMessage.from_dict(data)
        elif msg_type == MessageType.PROCESS_COMPLETE:
            return ProcessCompleteMessage.from_dict(data)
        elif msg_type == MessageType.COORDINATOR_READY:
            return CoordinatorReadyMessage.from_dict(data)
        
        return Message(msg_type, data["sender_id"], data.get("timestamp"))


class GGTValueMessage(Message):
    """Nachricht mit GGT-Wert zwischen Prozessen"""
    
    def __init__(self, sender_id: int, value: int):
        super().__init__(MessageType.GGT_VALUE, sender_id)
        self.value = value

    @staticmethod
    def from_dict(data: dict) -> 'GGTValueMessage':
        return GGTValueMessage(data["sender_id"], data["value"])


class AgentRegisterMessage(Message):
    """Agent registriert sich beim Coordinator"""
    
    def __init__(self, agent_id: int, capacity: int = 10):
        super().__init__(MessageType.AGENT_REGISTER, agent_id)
        self.capacity = capacity  # Maximale gleichzeitige Prozesse

    @staticmethod
    def from_dict(data: dict) -> 'AgentRegisterMessage':
        return AgentRegisterMessage(data["sender_id"], data.get("capacity", 10))


class AgentHeartbeatMessage(Message):
    """Regelmäßiger Heartbeat vom Agent mit Status"""
    
    def __init__(self, agent_id: int, active_processes: int):
        super().__init__(MessageType.AGENT_HEARTBEAT, agent_id)
        self.active_processes = active_processes

    @staticmethod
    def from_dict(data: dict) -> 'AgentHeartbeatMessage':
        return AgentHeartbeatMessage(data["sender_id"], data["active_processes"])


class StartProcessMessage(Message):
    """Coordinator beauftragt Agent, einen Prozess zu starten"""
    
    def __init__(self, coordinator_id: int, process_id: int, initial_value: int, 
                 predecessor_id: int, successor_id: int):
        super().__init__(MessageType.START_PROCESS, coordinator_id)
        self.process_id = process_id
        self.initial_value = initial_value
        self.predecessor_id = predecessor_id
        self.successor_id = successor_id

    @staticmethod
    def from_dict(data: dict) -> 'StartProcessMessage':
        return StartProcessMessage(
            data["sender_id"],
            data["process_id"],
            data["initial_value"],
            data["predecessor_id"],
            data["successor_id"]
        )


class ProcessCompleteMessage(Message):
    """Prozess meldet Abschluss und Ergebnis"""
    
    def __init__(self, agent_id: int, process_id: int, final_value: int):
        super().__init__(MessageType.PROCESS_COMPLETE, agent_id)
        self.process_id = process_id
        self.final_value = final_value

    @staticmethod
    def from_dict(data: dict) -> 'ProcessCompleteMessage':
        return ProcessCompleteMessage(data["sender_id"], data["process_id"], data["final_value"])


class CoordinatorReadyMessage(Message):
    """Coordinator meldet Bereitschaft zum Empfangen von Registrierungen"""
    
    def __init__(self, coordinator_id: int):
        super().__init__(MessageType.COORDINATOR_READY, coordinator_id)

    @staticmethod
    def from_dict(data: dict) -> 'CoordinatorReadyMessage':
        return CoordinatorReadyMessage(data["sender_id"])
