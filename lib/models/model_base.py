from typing import List, Any
from abc import ABC, abstractmethod
from lib.types import Action, Component, Information, Interpretation, Identifier
import threading


class Model(Component, ABC):
    def __init__(self, name: str):
        super().__init__(name)

    def send(self, raw_actions):
        for raw_action in raw_actions:
            if type(raw_action) is list:
                threads = [None] * len(raw_action)
                for i, r in enumerate(raw_action):
                    data = r["data"]
                    dest_ID = r["dest_ID"]
                    if data is not None or data != "":
                        # TODO: dont hardcode destination category
                        args = Action(self.dumpID(), Identifier(dest_ID, "Actuator"), r)
                        print("ARGS:", args)
                        threads[i] = threading.Thread(target=self.sendID,
                                                      args=(args,)
                                                      )
                        threads[i].start()
                # Wait for every thread to finish

                for i, r in enumerate(raw_action):
                    data = r["data"]
                    dest_ID = r["dest_ID"]
                    if data is not None or data != "":
                        threads[i].join()
            else:
                data = raw_action["data"]
                dest_ID = raw_action["dest_ID"]
                self.sendID(Action(self.dumpID(), Identifier(dest_ID, "Actuator"), raw_action))

    def put(self, data: Information) -> None:
        raw_actions = self.decide(data)
        if raw_actions is None or raw_actions == []:
            return
        self.send(raw_actions)

    @abstractmethod
    def decide(self, data: Interpretation) -> List[Any]:
        pass
