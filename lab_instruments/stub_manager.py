import hashlib
import json
import logging
from pathlib import Path
from typing import List, Set, Optional, Tuple
from datetime import datetime
from .registry import registry
# Configure logging
logger = logging.getLogger(__name__)

class StubManager:
    """Automatic type stub file management"""
    
    def __init__(self, package_dir: Path):
        self.package_dir = package_dir
        self.stub_file = package_dir / "__init__.pyi"
        self.cache_file = package_dir / ".stub_cache.json"
        self.plugins_dir = package_dir / "plugins"
        self.backup_dir = package_dir / ".stub_backups"
        self.generation_stats = {}
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
    
    def should_update_stub(self) -> Tuple[bool, str]:
        """Check if stub file needs updating"""
        if not self.stub_file.exists():
            return True, "Stub file does not exist"
        
        # Check for changes in plugins directory
        current_hash = self._get_plugins_hash()
        cached_hash = self._get_cached_hash()
        
        if current_hash != cached_hash:
            return True, "Plugin changes detected"
        
        # Check if registry has more devices than stub file
        current_devices = set(registry.list_devices())
        stub_devices = self._get_stub_devices()
        
        if current_devices != stub_devices:
            return True, f"Device registry mismatch (registry: {len(current_devices)}, stub: {len(stub_devices)})"
        
        return False, "No update needed"
    
    def update_stub_if_needed(self) -> bool:
        """Update stub file if needed"""
        should_update, reason = self.should_update_stub()
        if should_update:
            logger.info(f"Updating stub file: {reason}")
            success = self.generate_stub()
            self._save_cache()
            return success
        else:
            logger.debug(f"Stub file up to date: {reason}")
            return True
    
    def generate_stub(self) -> bool:
        """Generate type stub file"""
        generation_start = datetime.now()
        
        try:
            # Backup existing stub if it exists
            if self.stub_file.exists():
                self._backup_stub()
            
            devices = registry.list_devices()
            stub_content = self._generate_stub_content(devices)
            
            # Write stub file
            self.stub_file.write_text(stub_content, encoding='utf-8')
            
            # Update generation stats
            self.generation_stats = {
                'generated_at': generation_start.isoformat(),
                'duration': (datetime.now() - generation_start).total_seconds(),
                'devices_count': len(devices),
                'devices': devices,
                'stub_file_size': self.stub_file.stat().st_size,
                'success': True
            }
            
            logger.info(f"Generated stub file with {len(devices)} devices in {self.generation_stats['duration']:.3f}s")
            return True
            
        except Exception as e:
            self.generation_stats = {
                'generated_at': generation_start.isoformat(),
                'duration': (datetime.now() - generation_start).total_seconds(),
                'error': str(e),
                'success': False
            }
            logger.error(f"Failed to generate stub file: {e}")
            return False
    
    def _backup_stub(self):
        """Create backup of existing stub file"""
        if not self.stub_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"__init__.pyi.{timestamp}"
        
        try:
            backup_path.write_text(self.stub_file.read_text(encoding='utf-8'), encoding='utf-8')
            logger.debug(f"Created stub backup: {backup_path}")
            
            # Keep only last 5 backups
            self._cleanup_backups()
            
        except Exception as e:
            logger.warning(f"Failed to create stub backup: {e}")
    
    def _cleanup_backups(self, keep_count: int = 5):
        """Keep only the most recent backup files"""
        backup_files = list(self.backup_dir.glob("__init__.pyi.*"))
        if len(backup_files) <= keep_count:
            return
        
        # Sort by modification time, newest first
        backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Remove older backups
        for old_backup in backup_files[keep_count:]:
            try:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")
            except Exception as e:
                logger.warning(f"Failed to remove old backup {old_backup}: {e}")
    
    def _generate_stub_content(self, devices: List[str]) -> str:
        """Generate stub file content"""
        generation_time = datetime.now().isoformat()
        imports = []
        overloads = []
        typed_connects = []
        
        # Basic imports
        base_imports = [
            f"# Auto-generated stub file - {generation_time}",
            "# Do not edit manually - this file is automatically updated",
            "",
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
                typed_connects.append(f'def connect_{device}(method: str = None, plugins_dir: str = "lab_instruments/plugins", **kwargs) -> {class_name}: ...')
        
        all_imports = base_imports + imports
        imports_str = "\n".join(all_imports)
        overloads_str = "\n".join([f"@overload\n{overload}" for overload in overloads])
        typed_connects_str = "\n".join(typed_connects)
        
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

# Typed connect functions (auto-generated)
{typed_connects_str}

# Other exports
registry: object
CommonSCPI: type[CommonSCPI]
SCPIError: type[SCPIError]
'''
    
    def _get_stub_devices(self) -> Set[str]:
        """Extract device names from existing stub file"""
        if not self.stub_file.exists():
            return set()
        
        try:
            content = self.stub_file.read_text(encoding='utf-8')
            devices = set()
            
            # Parse Literal types from overloads
            import re
            pattern = r'def connect\(dev: Literal\["([^"]+)"\]'
            matches = re.findall(pattern, content)
            devices.update(matches)
            
            return devices
            
        except Exception as e:
            logger.warning(f"Failed to parse existing stub file: {e}")
            return set()
    
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
                        'scpi_size': scpi_file.stat().st_size,
                        'config_exists': config_file.exists(),
                        'config_mtime': config_file.stat().st_mtime if config_file.exists() else 0,
                        'config_size': config_file.stat().st_size if config_file.exists() else 0
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
            'last_updated': datetime.now().isoformat(),
            'plugins_hash': self._get_plugins_hash(),
            'devices': registry.list_devices(),
            'generation_stats': self.generation_stats
        }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.debug("Updated stub cache")
        except Exception as e:
            logger.warning(f"Failed to save stub cache: {e}")
    
    def get_generation_stats(self) -> dict:
        """Get stub generation statistics"""
        return self.generation_stats.copy()
    
    def get_cache_info(self) -> Optional[dict]:
        """Get cache file information"""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def force_regenerate(self) -> bool:
        """Force regeneration of stub file"""
        logger.info("Forcing stub file regeneration")
        success = self.generate_stub()
        self._save_cache()
        return success
    
    def cleanup(self):
        """Clean up temporary files and old backups"""
        try:
            # Clean old backups
            self._cleanup_backups(keep_count=3)
            
            # Remove cache if stub doesn't exist
            if not self.stub_file.exists() and self.cache_file.exists():
                self.cache_file.unlink()
                logger.debug("Removed orphaned cache file")
                
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

# Global instance
_package_dir = Path(__file__).parent
stub_manager = StubManager(_package_dir)
