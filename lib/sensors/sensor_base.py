from lib.types import Percept, Status, Component, Identifier
from abc import ABC, abstractmethod
from threading import Thread, Event
from typing import List, Any

TIMEOUT = 1.0


class Sensor(Component, ABC):
    """Class to generalize Sensors.

    Attributes:
        __perceiver (Thread): Thread that runs self.perceiver()
        waitable (bool): True if Sensor will wait for destination to signal to pause or continue
        wait_event: Event that will be evaluated in self.perceiver if waitable is true. Given that case, it will be set on or off if `resume()` or `pause()` functions are called.

    """
    def __init__(self, name: str, waitable: bool):
        super().__init__(name)
        self.__perceiver = Thread(target=self.perceiver)
        self.waitable = waitable
        self.wait_event = Event()
        self.status = Status.STOPPED

    def on(self) -> None:
        """
        Sets wait_event to allow processing and starts sense function in another thread.
        """
        self.status = Status.RUNNING
        self.wait_event.set()
        self.logger.info(f"{self.name} sensor is on.")
        self.__perceiver.start()

    def off(self) -> None:
        """
        Sets status to STOPPED and waits for the __perceiver Thread to join.
        """
        self.status = Status.STOPPED
        self.__perceiver.join(timeout=TIMEOUT)
        if self.__perceiver.is_alive():
            raise Exception(f"Sensor {self.name} wasn't shut down correctly.")
        self.logger.info(f"{self.name} sensor is off.")

    def send(self, raw_data):
        for dest_ID in self.get_destinations_ID(raw_data):
            self.sendID(Percept(self.dumpID(), dest_ID, raw_data))

    def resume(self):
        self.wait_event.set()
        self.status = Status.RUNNING
        self.reset_cache()

    def pause(self):
        self.wait_event.clear()
        self.status = Status.PAUSED
        self.reset_cache()

    def check_status(self):
        self.logger.info(f"SENSOR.IS_ALIVE(): {self.__perceiver.is_alive()}")

    def perceiver(self):
        """
        Reads and sends input. Waits if wait() method was called.
        """
        self.setup_perceiver()
        while True:
            if self.status == Status.STOPPED:
                break
            if self.waitable:
                self.wait_event.wait()
            data = self.read_input()
            if data is not None:
                self.send(data)
        self.close_perceiver()

    @abstractmethod
    def read_input(self) -> Any:
        pass

    @abstractmethod
    def reset_cache(self) -> Any:
        pass

    @abstractmethod
    def setup_perceiver(self) -> None:
        pass

    @abstractmethod
    def close_perceiver(self) -> None:
        pass
