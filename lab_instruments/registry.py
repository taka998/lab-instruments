from typing import Dict, Type, TypeVar, Generic, cast, Optional, Any, Callable
from pathlib import Path
import importlib
import json
import sys
import os
import logging
from datetime import datetime
from .core.scpi.common_scpi import CommonSCPI

T = TypeVar('T', bound=CommonSCPI)

# Configure logging
logger = logging.getLogger(__name__)
class DeviceInfo:
    """Device information storage class"""
    def __init__(self, name: str, device_class: Type[CommonSCPI], config_path: Optional[str] = None, 
                 plugin_path: Optional[str] = None, discovered_at: Optional[datetime] = None):
        self.name = name
        self.device_class = device_class
        self.config_path = config_path
        self.plugin_path = plugin_path
        self.discovered_at = discovered_at or datetime.now()
        self._config = None
        self._metadata = None
    
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
    
    @property
    def metadata(self) -> dict:
        """Get device metadata"""
        if self._metadata is None:
            self._metadata = {
                'name': self.name,
                'class_name': self.device_class.__name__,
                'module': self.device_class.__module__,
                'config_path': self.config_path,
                'plugin_path': self.plugin_path,
                'discovered_at': self.discovered_at.isoformat(),
                'has_config': bool(self.config_path and os.path.exists(self.config_path)),
                'methods': self._get_device_methods()
            }
        return self._metadata
    
    def _get_device_methods(self) -> list:
        """Get list of device-specific methods"""
        methods = []
        for attr_name in dir(self.device_class):
            if not attr_name.startswith('_'):
                attr = getattr(self.device_class, attr_name)
                if callable(attr):
                    methods.append({
                        'name': attr_name,
                        'doc': getattr(attr, '__doc__', '').strip() if hasattr(attr, '__doc__') else ''
                    })
        return methods
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate device configuration"""
        errors = []
        
        if not self.config_path or not os.path.exists(self.config_path):
            errors.append("Configuration file not found")
            return False, errors
        
        config = self.config
        if not config:
            errors.append("Configuration file is empty or invalid")
            return False, errors
        
        # Check required fields
        if 'method' not in config:
            errors.append("Missing 'method' in configuration")
        
        method = config.get('method', '').lower()
        if method not in ['serial', 'socket', 'visa']:
            errors.append(f"Invalid method '{method}'. Must be 'serial', 'socket', or 'visa'")
        
        # Method-specific validation
        if method == 'serial' and 'serial_params' not in config:
            errors.append("Missing 'serial_params' for serial method")
        elif method == 'socket' and 'socket_params' not in config:
            errors.append("Missing 'socket_params' for socket method")
        elif method == 'visa' and 'visa_params' not in config:
            errors.append("Missing 'visa_params' for visa method")
        
        return len(errors) == 0, errors

class DeviceRegistry:
    """Device registration and management system"""
    _devices: Dict[str, DeviceInfo] = {}
    _typed_connects: Dict[str, Callable] = {}
    _discovery_stats: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, name: str, device_class: Type[T], config_path: Optional[str] = None, 
                plugin_path: Optional[str] = None, discovered_at: Optional[datetime] = None) -> Type[T]:
        """Register a device class"""
        device_info = DeviceInfo(name, device_class, config_path, plugin_path, discovered_at)
        cls._devices[name] = device_info
        cls._typed_connects[name] = cls._create_typed_connect(name, device_class)
        
        logger.info(f"Registered device: {name} ({device_class.__name__})")
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
    def get_device_metadata(cls, name: str) -> Optional[dict]:
        """Get detailed device metadata"""
        info = cls.get_device_info(name)
        return info.metadata if info else None
    
    @classmethod
    def get_all_metadata(cls) -> Dict[str, dict]:
        """Get metadata for all registered devices"""
        return {name: info.metadata for name, info in cls._devices.items()}
    
    @classmethod
    def validate_device(cls, name: str) -> tuple[bool, list[str]]:
        """Validate a specific device configuration"""
        info = cls.get_device_info(name)
        if not info:
            return False, [f"Device '{name}' not found"]
        return info.validate_config()
    
    @classmethod
    def validate_all_devices(cls) -> Dict[str, tuple[bool, list[str]]]:
        """Validate all registered devices"""
        results = {}
        for name in cls.list_devices():
            results[name] = cls.validate_device(name)
        return results
    
    @classmethod
    def get_discovery_stats(cls) -> dict:
        """Get plugin discovery statistics"""
        return cls._discovery_stats.copy()
    
    @classmethod
    def clear_registry(cls):
        """Clear all registered devices (for testing)"""
        cls._devices.clear()
        cls._typed_connects.clear()
        cls._discovery_stats.clear()
        logger.info("Registry cleared")
    
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
        discovery_start = datetime.now()
        stats = {
            'start_time': discovery_start,
            'plugins_dir': plugins_dir,
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        plugins_path = Path(plugins_dir)
        if not plugins_path.exists():
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            stats['errors'].append(f"Plugins directory not found: {plugins_dir}")
            cls._discovery_stats = stats
            return
        
        logger.info(f"Starting plugin discovery in: {plugins_dir}")
        
        for device_dir in plugins_path.iterdir():
            if not device_dir.is_dir() or device_dir.name.startswith('.'):
                continue
            
            stats['attempted'] += 1
            success, error = cls._try_register_plugin(device_dir)
            if success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
                if error:
                    stats['errors'].append(f"{device_dir.name}: {error}")
        
        stats['end_time'] = datetime.now()
        stats['duration'] = (stats['end_time'] - discovery_start).total_seconds()
        cls._discovery_stats = stats
        
        logger.info(f"Plugin discovery completed: {stats['successful']}/{stats['attempted']} successful")
        if stats['failed'] > 0:
            logger.warning(f"Failed to register {stats['failed']} plugins")
    
    @classmethod
    def _try_register_plugin(cls, device_dir: Path) -> tuple[bool, Optional[str]]:
        """Try to register a plugin"""
        device_name = device_dir.name
        
        # Skip if already registered
        if device_name in cls._devices:
            return True, None
        
        try:
            # Check for SCPI class file existence
            scpi_file = device_dir / f"{device_name}_scpi.py"
            config_file = device_dir / "config.json"
            
            if not scpi_file.exists():
                return False, "SCPI file not found"
            
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
            cls.register(device_name, device_class, config_path, str(device_dir))
            
            return True, None
            
        except (ImportError, AttributeError, Exception) as e:
            error_msg = f"Registration failed: {str(e)}"
            logger.debug(f"Failed to register plugin {device_name}: {error_msg}")
            return False, error_msg

# Global registry instance
registry = DeviceRegistry()