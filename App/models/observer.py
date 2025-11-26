from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, record):
        """Called when a student record is updated"""
        pass
