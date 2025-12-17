import logging

from message import AgentRegisterMessage, GGTMessage, WorkerStartMessage

logger = logging.getLogger(__name__)


class MessageParser:
    @staticmethod
    def parse_ggt(raw: str):
        try:
            return GGTMessage.from_json(raw)
        except Exception as e:
            logger.error(f"Failed to parse GGT message: {e}")
            return None

    @staticmethod
    def parse_agent_register(raw: str):
        try:
            return AgentRegisterMessage.from_json(raw)
        except Exception as e:
            logger.error(f"Failed to parse AgentRegister message: {e}")
            return None

    @staticmethod
    def parse_worker_start(raw: str):
        try:
            return WorkerStartMessage.from_json(raw)
        except Exception as e:
            logger.error(f"Failed to parse WorkerStart message: {e}")
            return None
        
    @staticmethod
    def parse_result(raw: str):
        try:
            return WorkerStartMessage.from_json(raw)
        except Exception as e:
            logger.error(f"Failed to parse WorkerStart message: {e}")
            return None