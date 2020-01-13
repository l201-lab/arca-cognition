from lib.types import Interpretation, Identifier, Component, Information
from typing import List, Generator, Any
from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread, Event


def threaded(fx):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fx, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class Interpreter(Component, ABC):
    """Interpreter parent class.

    Attributes:
        name: A string that serves as an identifier for the Component.
        waitable: A boolean that indicates if the instance will have to wait
            for the answer of the forward connection.
    """
    def __init__(self, name: str, waitable: bool):
        super().__init__(name)
        self.queue = Queue()
        self.e = Event()
        self.waitable = waitable

    def put(self, data: Information) -> None:
        """External method that serves to put data to the percept queue."""
        self.queue.put(data)

    def send(self, raw_data: Any):
        """
        Decides destination given raw_data and calls Agent\'s sendID() to send
        such information to such destination.

        Args:
            raw_data: data to be sent.
        """
        for dest_ID in self.get_destinations_ID(raw_data):
            self.sendID(Interpretation(self.dumpID(), dest_ID, raw_data))

    @threaded
    def listen(self):
        """TODO: maybe listen shouldn't be threaded with a decorator"""

        while True:
            # Queue is suspended until there is something to read from the queu
            raw_data = self.queue.get()
            data = self.preprocess(raw_data.data)
            gen = self.process(data)
            stop = next(gen)
            self.logger.info(f"STOP: {stop}")
            if stop:
                self.sendID("PAUSE", raw_data.src)
                processed_data = next(gen)
                self.send(processed_data)
                if self.waitable:
                    self.e.wait()
                self.e.clear()
                self.logger.info("FINISHED WAITING, RESUMING SENSOR")
                self.sendID("RESUME", raw_data.src)
                with self.queue.mutex:
                    self.queue.queue.clear()

    @abstractmethod
    def preprocess(self, raw_data: Any) -> Any:
        """Given some raw_data, remove noise or add some useful metadata.

        Returns:
           Any: The preprocessed raw data.
        """
        pass

    @abstractmethod
    def process(self, raw_data) -> Generator:
        """
        Indicates (as soon as possible) if raw_data forms a significant
        composition or unit of perception and then returns the interpretation
        of such significant perception.

        Yields:
            bool: Indicates the sensor if it should stop (True) or continue listening (False).
            Any: Preprocessed data (if bool was True)
        """
        pass
