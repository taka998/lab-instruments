from abc import ABC, abstractmethod

class ConnectionInterface(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def write(self, command: str) -> None:
        pass

    @abstractmethod
    def read(self) -> str:
        pass

    @abstractmethod
    def query(self, command: str) -> str:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass
