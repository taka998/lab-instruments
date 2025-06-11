from core.interfaces import ConnectionInterface

class LCRSCPI:
    def __init__(self, connection: ConnectionInterface):
        self.conn = connection
