class SCPICommon:
    def __init__(self, connection):
        self.conn = connection

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

    def send(self, command):
        """Send arbitrary SCPI command"""
        self.conn.write(command)

    def query(self, command):
        """Send arbitrary SCPI command and read response"""
        return self.conn.query(command)
