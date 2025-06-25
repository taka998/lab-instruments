import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Set
from .registry import registry

class StubManager:
    """Automatic type stub file management"""
    
    def __init__(self, package_dir: Path):
        self.package_dir = package_dir
        self.stub_file = package_dir / "__init__.pyi"
        self.cache_file = package_dir / ".stub_cache.json"
        self.plugins_dir = package_dir / "plugins"
    
    def should_update_stub(self) -> bool:
        """Check if stub file needs updating"""
        if not self.stub_file.exists():
            return True
        
        # Check for changes in plugins directory
        current_hash = self._get_plugins_hash()
        cached_hash = self._get_cached_hash()
        
        return current_hash != cached_hash
    
    def update_stub_if_needed(self):
        """Update stub file if needed"""
        if self.should_update_stub():
            self.generate_stub()
            self._save_cache()
    
    def generate_stub(self):
        """Generate type stub file"""
        devices = registry.list_devices()
        stub_content = self._generate_stub_content(devices)
        
        # Write stub file
        self.stub_file.write_text(stub_content, encoding='utf-8')
    
    def _generate_stub_content(self, devices: List[str]) -> str:
        """Generate stub file content"""
        imports = []
        overloads = []
        
        # Basic imports
        base_imports = [
            "from typing import overload, Union, Literal",
            "from .core.scpi.common_scpi import CommonSCPI, SCPIError", 
            "from .core.interfaces import ConnectionInterface"
        ]
        
        # Plugin-specific imports and overloads
        for device in devices:
            device_info = registry.get_device_info(device)
            if device_info:
                class_name = device_info.device_class.__name__
                module_name = device_info.device_class.__module__
                
                # Convert absolute module path to relative
                if module_name.startswith('lab_instruments.'):
                    relative_module = '.' + module_name[len('lab_instruments.'):]
                else:
                    relative_module = module_name
                
                imports.append(f"from {relative_module} import {class_name}")
                overloads.append(f'def connect(dev: Literal["{device}"], method: str = None, plugins_dir: str = "lab_instruments/plugins", **kwargs) -> {class_name}: ...')
        
        all_imports = base_imports + imports
        imports_str = "\n".join(all_imports)
        overloads_str = "\n".join([f"@overload\n{overload}" for overload in overloads])
        
        return f'''{imports_str}

__version__: str

# Device-specific overloads
{overloads_str}

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
'''
    
    def _get_plugins_hash(self) -> str:
        """Generate hash from plugins directory content"""
        if not self.plugins_dir.exists():
            return ""
        
        plugin_info = {}
        for device_dir in self.plugins_dir.iterdir():
            if device_dir.is_dir() and not device_dir.name.startswith('.'):
                # Check existence of SCPI file and config file
                scpi_file = device_dir / f"{device_dir.name}_scpi.py"
                config_file = device_dir / "config.json"
                
                if scpi_file.exists():
                    plugin_info[device_dir.name] = {
                        'scpi_mtime': scpi_file.stat().st_mtime,
                        'config_exists': config_file.exists(),
                        'config_mtime': config_file.stat().st_mtime if config_file.exists() else 0
                    }
        
        # Convert dictionary to JSON and hash
        json_str = json.dumps(plugin_info, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _get_cached_hash(self) -> str:
        """Get cached hash"""
        if not self.cache_file.exists():
            return ""
        
        try:
            with open(self.cache_file) as f:
                cache_data = json.load(f)
                return cache_data.get('plugins_hash', '')
        except (json.JSONDecodeError, FileNotFoundError):
            return ""
    
    def _save_cache(self):
        """Save current state to cache"""
        cache_data = {
            'plugins_hash': self._get_plugins_hash(),
            'devices': registry.list_devices()
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

# Global instance
_package_dir = Path(__file__).parent
stub_manager = StubManager(_package_dir)