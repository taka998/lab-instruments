import json
import importlib
import sys
import os
from pathlib import Path

def parse_terminator(val):
    if isinstance(val, str):
        table = {
            'CR': '\r',
            'LF': '\n',
            'CRLF': '\r\n',
            'LFCR': '\n\r',
        }
        upper = val.upper()
        return table.get(upper, val)
    return val

def load_config(dev, plugins_dir):
    if plugins_dir == "plugins":
        current_dir = Path(__file__).parent
        plugins_dir = current_dir / "plugins"
    
    config_path = os.path.join(plugins_dir, dev, "config.json")
    if not os.path.isfile(config_path):
        raise ValueError(f'Config file for {dev} not found in {plugins_dir}.')
    with open(config_path) as f:
        return json.load(f)

def import_scpi_class(dev, plugins_dir):
    if plugins_dir == "plugins":
        try:
            module = importlib.import_module(f'lab_instruments.plugins.{dev}.{dev}_scpi')
            return getattr(module, f"{dev.upper()}SCPI")
        except (ModuleNotFoundError, AttributeError):
            pass
    
    abs_plugins_dir = os.path.abspath(plugins_dir)
    if abs_plugins_dir not in sys.path:
        sys.path.insert(0, abs_plugins_dir)
    try:
        module = importlib.import_module(f'{dev}.{dev}_scpi')
        return getattr(module, f"{dev.upper()}SCPI")
    except (ModuleNotFoundError, AttributeError):
        raise ImportError(f'SCPI class "{dev.upper()}SCPI" for {dev} not found in {plugins_dir}.')

def create_connection(method, config=None, kwargs=None):
    comm_method = (method or (config.get('method', '') if config else '')).lower()
    if comm_method == 'serial':
        from .interfaces import SerialConnection
        params = {**(config.get('serial_params', {}) if config else {}), **(kwargs or {})}
        if 'terminator' in params:
            params['terminator'] = parse_terminator(params['terminator'])
        return SerialConnection(**params)
    elif comm_method == 'socket':
        from .interfaces import SocketConnection
        params = {**(config.get('socket_params', {}) if config else {}), **(kwargs or {})}
        if 'terminator' in params:
            params['terminator'] = parse_terminator(params['terminator'])
        return SocketConnection(**params)
    elif comm_method == 'visa':
        from .interfaces import VisaConnection
        params = {**(config.get('visa_params', {}) if config else {}), **(kwargs or {})}
        if 'terminator' in params:
            params['terminator'] = parse_terminator(params['terminator'])
        return VisaConnection(**params)
    else:
        raise ValueError(f'Unknown method: {comm_method}')

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
        config = load_config(dev, plugins_dir)
        SCPIClass = import_scpi_class(dev, plugins_dir)
        conn = create_connection(method, config, kwargs)
        return SCPIClass(conn)
    else:
        comm_method = (method or '').lower()
        if comm_method not in ('serial', 'socket', 'visa'):
            raise ValueError('When dev is not specified, method must be "serial" or "socket" or "visa".')
        return create_connection(method, None, kwargs)
