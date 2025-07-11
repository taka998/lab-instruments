from ...core.scpi.common_scpi import CommonSCPI

class PLZ164WSCPI(CommonSCPI):
    def __init__(self, connection):
        super().__init__(connection)

    def load_on(self) -> None:
        self.s_send("OUTP ON")

    def load_off(self) -> None:
        self.s_send("OUTP OFF")

    def set_voltage(self, voltage) -> None:
        self.s_send(f"VOLT {voltage}")

    def set_current(self, current) -> None:
        self.s_send(f"CURR {current}")

    def set_over_power_protection(self, power) -> None:
        self.s_send(f"POW:PROT {power}")

    def get_voltage(self) -> float:
        res = self.s_query("MEAS:VOLT?")
        return float(res)

    def get_current(self) -> float:
        res = self.s_query("MEAS:CURR?")
        return float(res)
    
    def local(self) -> None:
        self.s_send("SYST:LOC")
