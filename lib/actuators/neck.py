from lib.actuators.actuator_base import Actuator
from lib.types import Action, Identifier
from subprocess import call
from typing import List, Any
import platform

class Neck(Actuator):
    def __init__(self, name: str):
        super().__init__(name)
        self.logger = self.get_logger()

    def do(self, action: Action) -> None:
        self.logger.info(f"{action.data}")

    def pass_msg(self, msg: str) -> None:
        pass

    def get_destinations_ID(self, raw_data: Any) -> List[Identifier]:
        pass

    def dump_history(self, filename: str, data: List[Any]) -> None:
        pass
