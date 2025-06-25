import os
import sys
import json

PLUGIN_TEMPLATE = '''from ...core.scpi.common_scpi import CommonSCPI

class {class_name}(CommonSCPI):
    def __init__(self, connection):
        super().__init__(connection)
'''

CONFIG_TEMPLATE = {
    "method": "serial",
    "serial_params": {
        "port": "/dev/ttyACM0",
        "baudrate": 9600,
        "timeout": 1.0,
        "terminator": "CRLF"
    },
    "socket_params": {
        "host": "192.168.0.10",
        "port": 1234,
        "timeout": 1.0,
        "terminator": "CRLF"
    },
    "visa_params": {
        "address": "USB0::0x0000::0x0000::INSTR",
        "timeout": 1.0,
        "terminator": "CRLF"
    }
}

def main():

    if len(sys.argv) == 2:
        name = sys.argv[1].lower()
    else:
        name = input("Enter plugin name: ").strip().lower()
        if not name:
            print("Plugin name is required.")
            sys.exit(1)
    class_name = f"{name.upper()}SCPI"
    plugin_dir = os.path.join("lab_instruments", "plugins", name)
    os.makedirs(plugin_dir, exist_ok=True)

    # Create __init__.py
    init_path = os.path.join(plugin_dir, "__init__.py")
    with open(init_path, "w") as f:
        pass

    # Create SCPI wrapper
    scpi_path = os.path.join(plugin_dir, f"{name}_scpi.py")
    with open(scpi_path, "w") as f:
        f.write(PLUGIN_TEMPLATE.format(class_name=class_name))

    # Create config.json
    config_path = os.path.join(plugin_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(CONFIG_TEMPLATE, f, indent=2)

    print(f"Plugin skeleton created at {plugin_dir}")

if __name__ == "__main__":
    main()
