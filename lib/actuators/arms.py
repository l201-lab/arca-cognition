from lib.actuators.actuator_base import Actuator
from lib.types import Action, Identifier
from subprocess import call
from typing import List, Any
import platform
import time

OS_ = platform.system()
if OS_ == "Linux":
    import serial

class Arms(Actuator):
    def __init__(self, name: str):
        super().__init__(name)
        self.logger = self.get_logger()
        if OS_ == "Linux":
            self.ser = serial.Serial(
               port='/dev/ttyS0',
               baudrate=9600
            )

    def do(self, action: Action) -> None:
        self.logger.info(f"{action.data}")
        if OS_ == "Linux":
            self.send_msg_serial(action.data["data"])

    def send_msg_serial(self, msg: str) -> None:
        self.ser.write(bytes(msg + "\n", encoding='utf-8'))

    def pass_msg(self, msg: str) -> None:
        pass

    def get_destinations_ID(self, raw_data: Any) -> List[Identifier]:
        pass

    def dump_history(self, filename: str, data: List[Any]) -> None:
        pass
