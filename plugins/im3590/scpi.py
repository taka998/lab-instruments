class IM3590:
    """
    SCPI command wrapper for Hioki IM3590.
    """

    def __init__(self, conn):
        self.conn = conn

    # --- Measurement Setup ---
    def set_mode(self, mode):
        """Set measurement mode :MEASure:MODE <MODE>"""
        self.conn.write(f":MEASure:MODE {mode}")

    def set_frequency(self, *freqs):
        """Set measurement frequencies :MEASure:FREQUENCY <freq1>,<freq2>,..."""
        freq_str = ",".join(map(str, freqs))
        self.conn.write(f":MEASure:FREQUENCY {freq_str}")

    def set_limit(self, limit):
        """Set judgment limit :MEASure:LIMIT <limit>"""
        self.conn.write(f":MEASure:LIMIT {limit}")

    def set_data_format(self, fmt):
        """Set data format :MEASure:DATA:FORMAT <format>"""
        self.conn.write(f":MEASure:DATA:FORMAT {fmt}")

    # --- Data Acquisition ---
    def measure(self):
        """:MEASure? Acquire measurement data"""
        return self.conn.query(":MEASure?")

    def set_continuous_execution(self, panel, onoff):
        """:CONTinuous:EXECution <panel>,<ON/OFF> Set continuous measurement"""
        self.conn.write(f":CONTinuous:EXECution {panel},{onoff}")

    def draw_continuous(self, mode):
        """:CONTinuous:DRAW <REAL/AFTer> Display continuous measurement"""
        self.conn.write(f":CONTinuous:DRAW {mode}")

    def set_trigger_condition(self, cond):
        """:MEASure:TRIGger Set trigger condition"""
        self.conn.write(f":MEASure:TRIGger {cond}")

    # --- Analysis & Processing ---
    def enable_filter(self, onoff):
        """:FILTER:ENABLE <ON/OFF> Enable/disable filter"""
        self.conn.write(f":FILTER:ENABLE {onoff}")

    def set_filter_param(self, param):
        """:FILTER:PARAM <param> Set filter parameter"""
        self.conn.write(f":FILTER:PARAM {param}")

    def get_comparator_result(self):
        """:MEASure:CONTinuous:COMParator? Get comparator result"""
        return self.conn.query(":MEASure:CONTinuous:COMParator?")

    def get_peak_result(self, mode="ALL"):
        """:MEASure:CONTinuous:PEAK? <mode> Get peak result"""
        return self.conn.query(f":MEASure:CONTinuous:PEAK? {mode}")

    # --- Device Control ---
    def reset_device(self):
        """:RESET Reset device"""
        self.conn.write(":RESET")

    def get_status(self):
        """:STATUS? Get device status"""
        return self.conn.query(":STATUS?")

    def set_system_date(self, date):
        """:SYSTEM:DATE Set system date"""
        self.conn.write(f":SYSTEM:DATE {date}")

    def help(self, command=None):
        """:HELP <command> Get command help"""
        if command:
            return self.conn.query(f":HELP {command}")
        return self.conn.query(":HELP")

    # --- Error Handling ---
    def get_error(self):
        """:ERROR? Get last error code"""
        return self.conn.query(":ERROR?")

    # --- System Management ---
    def get_panel_list(self):
        """:PANEL:LIST? Get list of panels"""
        return self.conn.query(":PANEL:LIST?")

    def set_panel_name(self, panel, name):
        """:PANEL:NAME <panel>,<name> Set panel name"""
        self.conn.write(f":PANEL:NAME {panel},{name}")

    def start_log(self, cond):
        """:LOG:START <cond> Start logging"""
        self.conn.write(f":LOG:START {cond}")

    def save_data(self, filename):
        """:SAVE:DATA <filename> Save data to file"""
        self.conn.write(f":SAVE:DATA {filename}")

    # --- Display & Format ---
    def set_display_format(self, fmt):
        """:DISPLAY:FORMAT <format> Set display format"""
        self.conn.write(f":DISPLAY:FORMAT {fmt}")

    def set_display_unit(self, unit):
        """:DISPLAY:UNIT <unit> Set display unit"""
        self.conn.write(f":DISPLAY:UNIT {unit}")

    def update_display(self, mode):
        """:DISPLAY:UPDATE <mode> Update display"""
        self.conn.write(f":DISPLAY:UPDATE {mode}")

    # --- Panel Management ---
    def get_panel_status(self, panel):
        """:PANEL:STATUS <panel> Get panel status"""
        return self.conn.query(f":PANEL:STATUS {panel}")

    # --- Filtering & Noise Reduction ---
    def set_filter_type(self, ftype):
        """:FILTER:TYPE <type> Set filter type"""
        self.conn.write(f":FILTER:TYPE {ftype}")

    # --- Miscellaneous ---
    def calibrate(self):
        """:CALIBRATE Calibrate device"""
        self.conn.write(":CALIBRATE")

    def start_sweep(self, start_freq, end_freq):
        """:SWEEP:START <start>,<end> Start frequency sweep"""
        self.conn.write(f":SWEEP:START {start_freq},{end_freq}")

    def set_trigger_source(self, source):
        """:TRIGger:SOURCE <source> Set trigger source"""
        self.conn.write(f":TRIGger:SOURCE {source}")
