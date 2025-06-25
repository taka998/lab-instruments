from typing import Optional, Union
from .core.connection_factory import create_connection, create_raw_connection
from .core.scpi.common_scpi import CommonSCPI
from .core.interfaces import ConnectionInterface
from .registry import registry
from .stub_manager import stub_manager

# Auto-discover plugins on module import
registry.auto_discover("lab_instruments/plugins")

# Update stub file if needed
stub_manager.update_stub_if_needed()

def _connect_device_via_registry(dev: str, method: Optional[str] = None, **kwargs) -> CommonSCPI:
    """Connect to device using registry information"""
    device_info = registry.get_device_info(dev.lower())
    if not device_info:
        raise ValueError(f'Device "{dev}" not found in registry. Available devices: {registry.list_devices()}')
    
    # Use config from registry
    config = device_info.config
    device_class = device_info.device_class
    
    # Create connection using config and user parameters
    effective_method = method or config.get('method', '')
    conn = create_connection(effective_method, config, kwargs)
    
    # Return typed instance
    return device_class(conn)

def connect(dev: Optional[str] = None, method: Optional[str] = None, plugins_dir: str = "lab_instruments/plugins", **kwargs) -> Union[CommonSCPI, ConnectionInterface]:
    """
    Factory function to initialize and return an appropriate SCPI wrapper instance or connection interface.
    
    - If dev is specified, loads device from registry and returns the typed SCPI wrapper.
    - If dev is not specified, returns a raw connection interface using method and kwargs.
    - User-supplied kwargs override config file parameters.
    - plugins_dir parameter is maintained for backward compatibility but registry is used internally.
    
    This function supports automatic type inference through generated stub files.
    """
    if dev:
        return _connect_device_via_registry(dev, method, **kwargs)
    else:
        return create_raw_connection(method, **kwargs)

def list_devices() -> list[str]:
    """Get list of available devices"""
    return registry.list_devices()

# Export typed connect functions for each registered device
def __getattr__(name: str):
    """Dynamic attribute access for typed connect functions"""
    if name.startswith('connect_'):
        device_name = name[8:]  # Remove 'connect_' prefix
        typed_connect = registry.get_typed_connect(device_name)
        if typed_connect:
            return typed_connect
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
