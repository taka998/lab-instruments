from core.scpi.common_scpi import CommonSCPI

class IM3590SCPI(CommonSCPI):
    def __init__(self, connection):
        super().__init__(connection)

    def set_parameter(self, idx, param):
        """
        Set display parameter.
        :param idx: Parameter index (1, 2, ...)
        :param param: Parameter string (e.g. Z, Y, PHASE, etc.)
        """
        self.conn.write(f":PARameter{idx} {param}")

    def get_parameter(self, idx):
        """
        Query display parameter.
        :param idx: Parameter index (1, 2, ...)
        :return: Parameter string
        """
        return self.conn.query(f":PARameter{idx}?")

    def set_range(self, range_no):
        """
        Set measurement range.
        :param range_no: Range number
        """
        self.conn.write(f":RANGe {range_no}")

    def get_range(self):
        """
        Query measurement range.
        :return: Range number
        """
        return self.conn.query(":RANGe?")

    def set_speed(self, speed):
        """
        Set measurement speed (e.g. FAST, MEDium, SLOW, SLOW2).
        :param speed: Speed string
        """
        self.conn.write(f":SPEEd {speed}")

    def get_speed(self):
        """
        Query measurement speed.
        :return: Speed string
        """
        return self.conn.query(":SPEEd?")

    def set_freq(self, freq):
        """
        Set measurement frequency.
        :param freq: Frequency value (Hz)
        """
        self.conn.write(f":FREQuency {freq}")

    def get_freq(self):
        """
        Query measurement frequency.
        :return: Frequency value (Hz)
        """
        return self.conn.query(":FREQuency?")

    def measure(self):
        """
        Query measurement value.
        :return: Measurement result string
        """
        return self.conn.query(":MEASure?")

    def set_mode(self, mode):
        """
        Set measurement mode (e.g. LCR, ANALyzer, CONTinuous).
        :param mode: Mode string
        """
        self.conn.write(f":MODE {mode}")

    def get_mode(self):
        """
        Query measurement mode.
        :return: Mode string
        """
        return self.conn.query(":MODE?")

