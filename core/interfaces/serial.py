import serial
from typing import Optional


class SerialConnection:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None

    def connect(self):
        if self.ser is not None and self.ser.is_open:
            return  # Already connected
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        except serial.SerialException as e:
            raise RuntimeError(f"Failed to open serial port: {e}")

    def disconnect(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
        self.ser = None

    def write(self, command):
        if not self.is_connected() or self.ser is None:
            raise RuntimeError("Serial port is not connected")
        self.ser.write((command + '\n').encode())

    def read(self):
        if not self.is_connected() or self.ser is None:
            raise RuntimeError("Serial port is not connected")
        return self.ser.readline().decode(errors='ignore').strip()

    def query(self, command):
        self.write(command)
        return self.read()

    def is_connected(self):
        return self.ser is not None and self.ser.is_open
