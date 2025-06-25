"""
Lab Instruments - SCPI device communication framework
"""
from .factory import connect, list_devices
from .registry import registry
from .core.scpi.common_scpi import CommonSCPI, SCPIError

__version__ = "1.0.0"
__all__ = [
    'connect',
    'list_devices', 
    'registry',
    'CommonSCPI',
    'SCPIError',
]

# Export typed connect functions dynamically
def __getattr__(name: str):
    """Dynamic attribute access for typed connect functions"""
    if name.startswith('connect_'):
        device_name = name[8:]  # Remove 'connect_' prefix
        typed_connect = registry.get_typed_connect(device_name)
        if typed_connect:
            return typed_connect
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")