from typing import overload, Union, Literal
from .core.scpi.common_scpi import CommonSCPI, SCPIError
from .core.interfaces import ConnectionInterface
from .plugins.plz164w.plz164w_scpi import PLZ164WSCPI
from .plugins.im3590.im3590_scpi import IM3590SCPI

__version__: str

# Device-specific overloads
@overload
def connect(dev: Literal["plz164w"], method: str = None, plugins_dir: str = "lab_instruments/plugins", **kwargs) -> PLZ164WSCPI: ...
@overload
def connect(dev: Literal["im3590"], method: str = None, plugins_dir: str = "lab_instruments/plugins", **kwargs) -> IM3590SCPI: ...

# Generic device (string)
@overload
def connect(dev: str, method: str = None, plugins_dir: str = "lab_instruments/plugins", **kwargs) -> CommonSCPI: ...

# Direct connection (no device specified)
@overload  
def connect(dev: None = None, method: str = ..., plugins_dir: str = "lab_instruments/plugins", **kwargs) -> ConnectionInterface: ...

def connect(dev = None, method = None, plugins_dir: str = "lab_instruments/plugins", **kwargs): ...

def list_devices() -> list[str]: ...

# Other exports
registry: object
CommonSCPI: type[CommonSCPI]
SCPIError: type[SCPIError]
