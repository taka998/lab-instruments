import json
import importlib
import sys
import os

def connect(dev=None, method=None, plugins_dir="plugins", **kwargs):
    """
    Factory function to initialize and return an appropriate SCPI wrapper instance or connection interface.
    - If dev is specified, loads config from {plugins_dir}/{dev}/config.json and returns the SCPI wrapper.
    - If dev is not specified, returns a raw connection interface (SerialConnection or SocketConnection) using method and kwargs.
    - User-supplied kwargs override config file parameters.
    - plugins_dir can be changed to support user-defined plugins.
    Raises ValueError or ImportError on failure.
    """
    dev = dev.lower() if dev else None

    if dev:
        config_path = os.path.join(plugins_dir, dev, "config.json")
        if not os.path.isfile(config_path):
            raise ValueError(f'Config file for {dev} not found in {plugins_dir}.')
        with open(config_path) as f:
            config = json.load(f)

        # Add plugins_dir to sys.path if not already present
        abs_plugins_dir = os.path.abspath(plugins_dir)
        if abs_plugins_dir not in sys.path:
            sys.path.insert(0, abs_plugins_dir)

        # Import SCPI wrapper class dynamically
        try:
            module = importlib.import_module(f'{dev}.{dev}_scpi')
            SCPIClass = getattr(module, f"{dev.upper()}SCPI")
        except (ModuleNotFoundError, AttributeError):
            raise ImportError(f'SCPI class \"{dev.upper()}SCPI\" for {dev} not found in {plugins_dir}.')

        comm_method = (method or config.get('method', '')).lower()
        if comm_method == 'serial':
            from core.interfaces.serial_interface import SerialConnection
            params = {**config.get('serial_params', {}), **kwargs}
            conn = SerialConnection(**params)
        elif comm_method == 'socket':
            from core.interfaces.socket_interface import SocketConnection
            params = {**config.get('socket_params', {}), **kwargs}
            conn = SocketConnection(**params)
        else:
            raise ValueError(f'Unknown method: {comm_method}')
        return SCPIClass(conn)
    else:
        comm_method = (method or '').lower()
        if comm_method == 'serial':
            from core.interfaces.serial_interface import SerialConnection
            return SerialConnection(**kwargs)
        elif comm_method == 'socket':
            from core.interfaces.socket_interface import SocketConnection
            return SocketConnection(**kwargs)
        else:
            raise ValueError('When dev is not specified, method must be "serial" or "socket".')
