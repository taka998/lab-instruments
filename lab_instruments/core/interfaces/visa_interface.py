import pyvisa
from .connection import (
    ConnectionInterface,
    ConnectionClosedError,
    ConnectionIOError,
)

class VisaConnection(ConnectionInterface):
    def __init__(self, address: str, timeout: float = 1.0, terminator: str = '\n'):
        self.address = address
        self.timeout = timeout
        self.terminator = terminator
        self.rm = None
        self.inst = None

    def connect(self):
        if self.inst is not None:
            return
        try:
            self.rm = pyvisa.ResourceManager()
            self.inst = self.rm.open_resource(self.address)
            self.inst.timeout = int(self.timeout * 1000)  # ms
            self.inst.write_termination = self.terminator
            self.inst.read_termination = self.terminator
        except pyvisa.VisaIOError as e:
            raise ConnectionIOError(f"VISA open error: {e}")

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
        self.inst = None
        self.rm = None

    def write(self, command: str):
        if not self.is_connected():
            raise ConnectionClosedError("VISA not connected")
        try:
            self.inst.write(command)
        except pyvisa.VisaIOError as e:
            raise ConnectionIOError(f"VISA write error: {e}")

    def read(self) -> str:
        if not self.is_connected():
            raise ConnectionClosedError("VISA not connected")
        try:
            return self.inst.read().strip()
        except pyvisa.VisaIOError as e:
            raise ConnectionIOError(f"VISA read error: {e}")

    def query(self, command: str) -> str:
        if not self.is_connected():
            raise ConnectionClosedError("VISA not connected")
        try:
            return self.inst.query(command).strip()
        except pyvisa.VisaIOError as e:
            raise ConnectionIOError(f"VISA query error: {e}")

    def is_connected(self) -> bool:
        return self.inst is not None
