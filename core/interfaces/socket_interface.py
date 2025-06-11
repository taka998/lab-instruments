from .connection import ConnectionInterface
import socket
from typing import Optional

class SocketConnection(ConnectionInterface):
    def __init__(self, host: str, port: int, timeout: float = 1.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None

    def connect(self):
        if self.sock is not None:
            return  # Already connected
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except OSError as e:
            raise RuntimeError(f"Failed to open socket: {e}")

    def disconnect(self):
        if self.sock is not None:
            self.sock.close()
        self.sock = None

    def write(self, command: str):
        if not self.is_connected() or self.sock is None:
            raise RuntimeError("Socket is not connected")
        self.sock.sendall((command + '\n').encode())

    def read(self) -> str:
        if not self.is_connected() or self.sock is None:
            raise RuntimeError("Socket is not connected")
        data = b''
        while not data.endswith(b'\n'):
            chunk = self.sock.recv(1024)
            if not chunk:
                break
            data += chunk
        return data.decode(errors='ignore').strip()

    def query(self, command: str):
        self.write(command)
        return self.read()

    def is_connected(self):
        return self.sock is not None
