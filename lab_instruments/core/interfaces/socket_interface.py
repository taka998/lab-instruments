import socket
from typing import Optional
from .connection import ( 
    ConnectionInterface,
    ConnectionTimeoutError,
    ConnectionIOError,
    ConnectionClosedError,
)

class SocketConnection(ConnectionInterface):
    def __init__(self, host: str, port: int, timeout: float = 1.0, terminator: str = "\r\n"):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.terminator = terminator
        self.sock: Optional[socket.socket] = None

    def connect(self):
        if self.sock is not None:
            return  # Already connected
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except socket.timeout as e:
            raise ConnectionTimeoutError(f"Socket connect timeout: {e}")
        except OSError as e:
            raise ConnectionIOError(f"Failed to open socket: {e}")

    def disconnect(self):
        try:
            if self.sock is not None:
                self.sock.close()
        except OSError as e:
            raise ConnectionIOError(f"Failed to close socket: {e}")
        self.sock = None

    def write(self, command: str):
        if not self.is_connected() or self.sock is None:
            raise ConnectionClosedError("Socket is not connected")
        try:
            self.sock.sendall((command + self.terminator).encode())
        except socket.timeout as e:
            raise ConnectionTimeoutError(f"Socket write timeout: {e}")
        except OSError as e:
            raise ConnectionIOError(f"Socket write error: {e}")

    def read(self) -> str:
        if not self.is_connected() or self.sock is None:
            raise ConnectionClosedError("Socket is not connected")
        data = b''
        terminator_bytes = self.terminator.encode()
        try:
            while not data.endswith(terminator_bytes):
                chunk = self.sock.recv(1024)
                if not chunk:
                    break
                data += chunk
        except socket.timeout as e:
            raise ConnectionTimeoutError(f"Socket read timeout: {e}")
        except OSError as e:
            raise ConnectionIOError(f"Socket read error: {e}")
        return data.decode(errors='ignore').strip()

    def query(self, command: str):
        self.write(command)
        return self.read()

    def is_connected(self):
        return self.sock is not None
