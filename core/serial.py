import serial

class SerialConnection:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def write(self, command):
        self.ser.write((command + '\n').encode())

    def read(self):
        return self.ser.readline().decode().strip()

    def query(self, command):
        self.write(command)
        return self.read()

    def is_connected(self):
        return self.ser is not None and self.ser.is_open
