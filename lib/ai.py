from lib.types import Component, Information, Identifier, NestedDefaultDict
from lib.sensors.sensor_base import Sensor
from lib.interpreters.interpreter_base import Interpreter
from lib.models.model_base import Model
from lib.actuators.actuator_base import Actuator
from lib.observers.observer_base import Subject, Observer
from typing import Dict, List, Union, Optional
from lib.utilities.helpers import create_path, get_date, setup_logger
import pprint
pp = pprint.PrettyPrinter(indent=4)


class Agent(Subject):
    """Class to generalize Agents.

    Attributes:
        name (str): name of the agent
        actuators (Dict[str, Actuator]): collection of Actuators
        sensors (Dict[str, Sensor]): collection of Sensors
        interpreters (Dict[str, Interpreter]): collection of Interpreters
        models (Dict[str, Model]): collection of Models
        observers (List[Observer]): collection of Observers (DP)
        history (NestedDefaultDict): Stores messages from source Component to destination Component in structure `src.category/src.name/dest.category/dest.name`.
    """

    name: str = ""
    actuators: Dict[str, Actuator] = {}
    sensors: Dict[str, Sensor] = {}
    interpreters: Dict[str, Interpreter] = {}
    models: Dict[str, Model] = {}
    observers: List[Observer] = []
    history = NestedDefaultDict()

    def __init__(self, name: str):
        self.name = name
        self.logger = setup_logger(f"{name}",
                                   f"logs/Agent/{name}/{get_date()}.txt")

    def shutdown(self) -> None:
        """
        Dumps history and shuts off every sensor.
        """
        self.logger.info(f"Shutting down {self.name}")
        self.dump_history()
        for s_name, sensor in self.sensors.items():
            sensor.off()
        self.logger.info(f"Done.")

    def add_component(self, e: Component) -> None:
        """
        Takes a component and appends it to its corresponding collection.
        """
        fwdlist = {
            "Sensor": self.sensors,
            "Interpreter": self.interpreters,
            "Model": self.models,
            "Actuator": self.actuators
        }
        self.logger.info(
            f"Adding Component {e.dumpID().category}:{e.dumpID().name}.")
        fwdlist[e.dumpID().category][e.dumpID().name] = e

    def attach_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def detach_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def notify_observers(self, keyword: str) -> None:
        for obs in self.observers:
            obs.update(self, keyword)

    def sendID(self,
               msg: Union[Information, str],
               rcv: Optional[Component] = None) -> None:
        """
        Callback function that is executed in an Component to pass a msg (can be Information or just a string) to another Component.

        Args:
            msg (Union[Information, str]): message can be a Percept, Interpretation, Action or string.
            rcv (Optional[Component]): receiver might be optional, since Information already contains such data.

        Returns:
            None
        """

        fwdlist = {
            "Sensor": self.sensors,
            "Interpreter": self.interpreters,
            "Model": self.models,
            "Actuator": self.actuators
        }
        if isinstance(msg, Information):
            self.logger.info(
                f"Information is passed from {msg.src.name} to {msg.dest.name}."
            )
            fwdlist[msg.dest.category][msg.dest.name].put(msg)
            self.history[msg.src.category][msg.src.name][msg.dest.category][
                msg.dest.name].append(msg.data)
        elif isinstance(msg, str):
            if rcv is None:
                raise Exception(
                    "If message is a string, a receiver must be specified.")
            self.logger.info(f"MESSAGE {msg} was passed to {rcv.name}.")
            fwdlist[rcv.category][rcv.name].pass_msg(msg)

    def associate(self, src: Component, dest: Component) -> None:
        """
        Adds dest destination to src Component and defines src's sendID() with Agent's sendID().
        """
        self.logger.info(
            f"Associating {src.dumpID().category}:{src.dumpID().name} with {dest.dumpID().category}:{dest.dumpID().name}"
        )
        src.add_destination_ID(dest.dumpID())
        src.sendID = self.sendID
        self.history[src.dumpID().category][src.dumpID().name][
            dest.dumpID().category][dest.dumpID().name] = []

    def dump_history(self) -> None:
        """
        Calls every Component's dump_history with their corresponding data stored in self.history.
        """
        fwdlist = {
            "Sensor": self.sensors,
            "Interpreter": self.interpreters,
            "Model": self.models,
            "Actuator": self.actuators
        }
        for src_cat, src_catv in self.history.items():
            for src_name, src_namev in src_catv.items():
                for dest_cat, dest_catv in src_namev.items():
                    for dest_name, data in dest_catv.items():
                        path = f"logs/{src_cat}/{src_name}/{dest_cat}/{dest_name}"
                        create_path(path)
                        timestamp = get_date()
                        fwdlist[src_cat][src_name].dump_history(
                            f"{path}/{timestamp}", data)
