from typing import Dict, Type, TypeVar, Generic, cast, Optional, Any, Callable
from pathlib import Path
import importlib
import json
import sys
import os
from .core.scpi.common_scpi import CommonSCPI

T = TypeVar('T', bound=CommonSCPI)

class DeviceInfo:
    """Device information storage class"""
    def __init__(self, name: str, device_class: Type[CommonSCPI], config_path: Optional[str] = None):
        self.name = name
        self.device_class = device_class
        self.config_path = config_path
        self._config = None
    
    @property
    def config(self) -> dict:
        """Lazy load configuration file"""
        if self._config is None and self.config_path:
            try:
                with open(self.config_path) as f:
                    self._config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self._config = {}
        return self._config or {}

class DeviceRegistry:
    """Device registration and management system"""
    _devices: Dict[str, DeviceInfo] = {}
    _typed_connects: Dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: str, device_class: Type[T], config_path: Optional[str] = None) -> Type[T]:
        """Register a device class"""
        device_info = DeviceInfo(name, device_class, config_path)
        cls._devices[name] = device_info
        cls._typed_connects[name] = cls._create_typed_connect(name, device_class)
        return device_class
    
    @classmethod
    def get_device_info(cls, name: str) -> Optional[DeviceInfo]:
        """Get device information"""
        return cls._devices.get(name)
    
    @classmethod
    def get_device_class(cls, name: str) -> Optional[Type[CommonSCPI]]:
        """Get device class"""
        info = cls.get_device_info(name)
        return info.device_class if info else None
    
    @classmethod
    def get_typed_connect(cls, name: str) -> Optional[Callable]:
        """Get typed connect function"""
        return cls._typed_connects.get(name)
    
    @classmethod
    def list_devices(cls) -> list[str]:
        """Get list of registered devices"""
        return list(cls._devices.keys())
    
    @classmethod
    def _create_typed_connect(cls, name: str, device_class: Type[T]) -> Callable[..., T]:
        """Generate typed connect function"""
        def typed_connect(method: Optional[str] = None, plugins_dir: str = "lab_instruments/plugins", **kwargs) -> T:
            from lab_instruments.factory import connect_device
            return cast(T, connect_device(name, method, plugins_dir, **kwargs))
        
        # Set function name and documentation
        typed_connect.__name__ = f"connect_{name}"
        typed_connect.__doc__ = f"Create a typed connection to {name} device.\n\nReturns: {device_class.__name__}"
        
        return typed_connect
    
    @classmethod
    def auto_discover(cls, plugins_dir: str = "lab_instruments/plugins") -> None:
        """Auto-scan plugins directory and register devices"""
        plugins_path = Path(plugins_dir)
        if not plugins_path.exists():
            return
        
        for device_dir in plugins_path.iterdir():
            if not device_dir.is_dir() or device_dir.name.startswith('.'):
                continue
            
            cls._try_register_plugin(device_dir)
    
    @classmethod
    def _try_register_plugin(cls, device_dir: Path) -> None:
        """Try to register a plugin"""
        device_name = device_dir.name
        
        # Skip if already registered
        if device_name in cls._devices:
            return
        
        try:
            # Check for SCPI class file existence
            scpi_file = device_dir / f"{device_name}_scpi.py"
            config_file = device_dir / "config.json"
            
            if not scpi_file.exists():
                return
            
            # Add plugins directory to sys.path if needed
            plugins_parent = device_dir.parent
            abs_plugins_dir = os.path.abspath(plugins_parent)
            if abs_plugins_dir not in sys.path:
                sys.path.insert(0, abs_plugins_dir)
            
            # Dynamic import
            module_path = f"lab_instruments.plugins.{device_name}.{device_name}_scpi"
            module = importlib.import_module(module_path)
            
            # Get SCPI class
            class_name = f"{device_name.upper()}SCPI"
            device_class = getattr(module, class_name)
            
            # Register
            config_path = str(config_file) if config_file.exists() else None
            cls.register(device_name, device_class, config_path)
            
        except (ImportError, AttributeError, Exception) as e:
            # Ignore registration failures (uncomment for debugging)
            # print(f"Failed to register plugin {device_name}: {e}")
            pass

# Global registry instance
registry = DeviceRegistry()