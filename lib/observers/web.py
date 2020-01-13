from lib.observers.observer_base import Observer, Subject
from multiprocessing import Process
from lib.observers.server import execute


class WebInterface(Observer):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.process = Process(
            target=execute, kwargs={
                "host": host,
                "port": port
            })

    def activate(self):
        self.process.start()

    def deactivate(self):
        self.process.terminate()

    def update(self, subject: Subject, keyword: str):
        pass
