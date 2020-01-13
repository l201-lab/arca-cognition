from lib.types import Action, Component
from abc import ABC, abstractmethod


class Actuator(Component, ABC):
    def __init__(self, name):
        super().__init__(name)

    def put(self, action: Action) -> None:
        self.do(action)

    @abstractmethod
    def do(self, action: Action) -> None:
        pass
