import json


class GGTMessage:
    def __init__(self, sender_id: int, value: int):
        self.sender_id = sender_id
        self.value = value

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(text: str):
        data = json.loads(text)
        return GGTMessage(
            sender_id=data["sender_id"],
            value=data["value"],
        )


class AgentRegisterMessage:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(text: str):
        data = json.loads(text)
        return AgentRegisterMessage(agent_id=data["agent_id"])


class WorkerStartMessage:
    def __init__(self, process_id: int, initial_value: int, pred: int, succ: int):
        self.process_id = process_id
        self.initial_value = initial_value
        self.pred = pred
        self.succ = succ

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(text: str):
        data = json.loads(text)
        return WorkerStartMessage(
            process_id=data["process_id"],
            initial_value=data["initial_value"],
            pred=data["pred"],
            succ=data["succ"],
        )
