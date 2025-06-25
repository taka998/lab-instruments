from .factory import connect
from .scpi.common_scpi import CommonSCPI, SCPIError

__version__ = "1.0.0"
__all__ = [
    'connect',
    'CommonSCPI', 
    'SCPIError',
]
