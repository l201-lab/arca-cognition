from abc import ABC, abstractmethod


class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach_observer(self, observer: 'Observer') -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach_observer(self, observer: 'Observer') -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify_observers(self) -> None:
        """
        Notify all observers about an event.
        """
        pass


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Receive update from subject.
        """
        pass
