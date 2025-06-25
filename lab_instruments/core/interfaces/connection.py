from abc import ABC, abstractmethod

class ConnectionInterface(ABC):
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

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

class ConnectionError(Exception):
    pass

class ConnectionClosedError(ConnectionError):
    pass

class ConnectionTimeoutError(ConnectionError):
    pass

class ConnectionIOError(ConnectionError):
    pass

class ConnectionProtocolError(ConnectionError):
    pass
