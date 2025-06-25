
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

def create_connection(method, config=None, kwargs=None):
    """Create connection interface based on method and parameters"""
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

def create_raw_connection(method, **kwargs):
    """Create raw connection interface without device-specific wrapper"""
    comm_method = (method or '').lower()
    if comm_method not in ('serial', 'socket', 'visa'):
        raise ValueError('Method must be "serial", "socket", or "visa".')
    return create_connection(method, None, kwargs)
