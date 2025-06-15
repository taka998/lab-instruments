from core.scpi.common_scpi import CommonSCPI

class IM3590SCPI(CommonSCPI):
    def __init__(self, connection):
        super().__init__(connection)
