import serial
from typing import Optional
from .connection import(
    ConnectionInterface,
    ConnectionClosedError,
    ConnectionIOError,
    ConnectionTimeoutError,
) 

class SerialConnection(ConnectionInterface):
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 9600, timeout: float = 1.0, terminator: str = "\r\n"):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.terminator = terminator
        self.ser: Optional[serial.Serial] = None

    def connect(self):
        if self.ser is not None and self.ser.is_open:
            return
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        except serial.SerialException as e:
            raise ConnectionIOError(f"Failed to open serial port: {e}")

    def disconnect(self):
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.close()
        except serial.SerialException as e:
            raise ConnectionIOError(f"Failed to close serial port: {e}")
        self.ser = None

    def write(self, command):
        if not self.is_connected() or self.ser is None:
            raise ConnectionClosedError("Serial port is not connected")
        try:
            self.ser.write((command + self.terminator).encode())
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeoutError(f"Serial write timeout: {e}")
        except serial.SerialException as e:
            raise ConnectionIOError(f"Serial write error: {e}")

    def read(self):
        if not self.is_connected() or self.ser is None:
            raise ConnectionClosedError("Serial port is not connected")
        try:
            return self.ser.readline().decode(errors='ignore').strip()
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeoutError(f"Serial read timeout: {e}")
        except serial.SerialException as e:
            raise ConnectionIOError(f"Serial read error: {e}")

    def query(self, command):
        self.write(command)
        return self.read()

    def is_connected(self):
        return self.ser is not None and self.ser.is_open
