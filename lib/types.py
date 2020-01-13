from enum import Enum, auto
from typing import Callable, List, Any
from abc import ABC, abstractmethod
from collections import defaultdict
from lib.utilities.helpers import setup_logger, get_date


class Status(Enum):
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


class Identifier:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category

    def to_tuple(self):
        return self.name, self.category
    def __str__(self):
        return f"(ID: {self.name}, {self.category})"


class Information:
    pass


class Component(ABC):
    """
    Defines general behavior of Sensors, Interpreters, Models and Actuators.

    Attributes:
        name (str): Self-descriptor
        destinations_ID: (List[Interpreter]): list of the IDs of possible destinations
        sendID (Callable): Agent's function/callback to pass a message to another Component given its Identifier
    """
    def __init__(self, name):
        self.name: str = name
        self.destinations_ID: List[Identifier] = []
        self.sendID: Callable

    def add_destination_ID(self, dest_ID: Identifier):
        self.destinations_ID.append(dest_ID)

    def dumpID(self) -> Identifier:
        base_class = self.__class__.__bases__[0].__name__
        return Identifier(self.name, base_class)

    def get_logger(self):
        name, cat = self.dumpID().to_tuple()
        return setup_logger(f"{cat}.{name}",
                            f"logs/{cat}/{name}/{get_date()}.txt")

    @abstractmethod
    def get_destinations_ID(self, raw_data) -> List[Identifier]:
        """Given some data, decide destination. Must handle None/empty data."""
        pass

    @abstractmethod
    def dump_history(self, _id: Identifier, history: List[Any]) -> None:
        pass

    @abstractmethod
    def pass_msg(self, msg: str) -> None:
        pass


class Percept(Information):
    def __init__(self, src: Identifier, dest: Identifier, data):
        self.src = src
        self.dest = dest
        self.data = data


class Interpretation(Information):
    def __init__(self, src: Identifier, dest: Identifier, data):
        self.src = src
        self.dest = dest
        self.data = data


class Action(Information):
    def __init__(self, src: Identifier, dest: Identifier, data):
        self.src = src
        self.dest = dest
        self.data = data
    def __str__(self):
        return f"{self.data}, {self.src}, {self.dest}"


class NestedDefaultDict(defaultdict):
    def __init__(self, *args, **kwargs):
        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args,
                                                **kwargs)

    def __repr__(self):
        return repr(dict(self))
