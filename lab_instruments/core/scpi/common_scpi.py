import time
from ..interfaces import ConnectionInterface

class CommonSCPI:
    def __init__(self, connection: ConnectionInterface):
        self.conn = connection

    def __enter__(self):
        self.conn.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.__exit__(exc_type, exc_val, exc_tb)

    def idn(self):
        """*IDN? Identification query"""
        return self.conn.query("*IDN?")

    def reset(self):
        """*RST Reset instrument"""
        self.conn.write("*RST")

    def clear_status(self):
        """*CLS Clear status"""
        self.conn.write("*CLS")

    def opc(self):
        """*OPC Set operation complete bit"""
        self.conn.write("*OPC")

    def opc_query(self):
        """*OPC? Wait for operation complete"""
        return self.conn.query("*OPC?")

    def esr_query(self):
        """*ESR? Read standard event status register"""
        return self.conn.query("*ESR?")

    def stb_query(self):
        """*STB? Read status byte"""
        return self.conn.query("*STB?")

    def sre(self, value):
        """*SRE Set service request enable register"""
        self.conn.write(f"*SRE {value}")

    def sre_query(self):
        """*SRE? Query service request enable register"""
        return self.conn.query("*SRE?")

    def ese(self, value):
        """*ESE <data> Set standard event status enable register"""
        self.conn.write(f"*ESE {value}")

    def ese_query(self):
        """*ESE? Query standard event status enable register"""
        return self.conn.query("*ESE?")

    def opt_query(self):
        """*OPT? Query installed options"""
        return self.conn.query("*OPT?")

    def psc(self, value):
        """*PSC ON|OFF|1|0 Set power-on status clear"""
        self.conn.write(f"*PSC {value}")

    def psc_query(self):
        """*PSC? Query power-on status clear setting"""
        return self.conn.query("*PSC?")

    def rcl(self, filename):
        """*RCL "<filename>" Recall configuration from file"""
        self.conn.write(f'*RCL "{filename}"')

    def sav(self, filename):
        """*SAV "<filename>" Save configuration to file"""
        self.conn.write(f'*SAV "{filename}"')

    def trg(self):
        """*TRG Trigger instrument"""
        self.conn.write("*TRG")

    def tst_query(self):
        """*TST? Self-test query"""
        return self.conn.query("*TST?")

    def wai(self):
        """*WAI Wait-to-continue"""
        self.conn.write("*WAI")

    def send(self, command, safe=True, timeout=5.0, interval=0.1):
        """
        Send a SCPI command. If safe=True, monitors completion and errors using *OPC and *ESR?.
        """
        self.conn.write(command)
        if not safe:
            return
        self.conn.write("*OPC")
        start = time.time()
        while True:
            esr_str = self.conn.query("*ESR?")
            try:
                esr = int(esr_str)
            except Exception:
                raise SCPIError(-1, f"Failed to parse ESR value: '{esr_str}'")
            if esr & 0b10:  # Operation Complete (bit 1)
                if esr & ~0b10:
                    raise SCPIError(esr)
                break
            if timeout != 0.0:
                if time.time() - start > timeout:
                    raise TimeoutError("SCPI command did not complete in time (OPC/ESR)")
            time.sleep(interval)

    def query(self, command, safe=True, timeout=5.0, interval=0.1):
        """
        Send a SCPI query command and get the response. If safe=True, monitors completion and errors using *OPC and *ESR?.
        """
        response = self.conn.query(command)
        if not safe:
            return
        self.conn.write("*OPC")
        start = time.time()
        while True:
            esr_str = self.conn.query("*ESR?")
            try:
                esr = int(esr_str)
            except Exception:
                raise SCPIError(-1, f"Failed to parse ESR value: '{esr_str}'")
            if esr & 0b10:  # Operation Complete (bit 1)
                if esr & ~0b10:
                    raise SCPIError(esr)
                break
            if timeout != 0.0:
                if time.time() - start > timeout:
                    raise TimeoutError("SCPI command did not complete in time (OPC/ESR)")
            time.sleep(interval)
        return response

class SCPIError(Exception):
    """
    Exception for SCPI errors, decoding ESR value into human-readable messages.
    """
    ESR_MEANINGS = [
        "Operation Complete",      # bit 0 (1)
        "Request Control",         # bit 1 (2)
        "Query Error",             # bit 2 (4)
        "Device Dependent Error",  # bit 3 (8)
        "Execution Error",         # bit 4 (16)
        "Command Error",           # bit 5 (32)
        "User Request",            # bit 6 (64)
        "Power On"                 # bit 7 (128)
    ]

    def __init__(self, esr_value, message=None):
        self.esr_value = esr_value
        self.flags = self.decode_esr(esr_value)
        msg = message or self.format_message(esr_value, self.flags)
        super().__init__(msg)

    @classmethod
    def decode_esr(cls, esr_value):
        """Return a list of ESR flag meanings for the given value."""
        flags = []
        for i, name in enumerate(cls.ESR_MEANINGS):
            if (esr_value >> i) & 1:
                flags.append(name)
        return flags

    @staticmethod
    def format_message(esr_value, flags):
        if not flags:
            return f"SCPI Error: ESR={esr_value} (No error flags set)"
        return f"SCPI Error: ESR={esr_value} (Flags: {', '.join(flags)})"
