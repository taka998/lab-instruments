#!/usr/bin/env python3
"""
Lab Instruments System Diagnostics Tool
システム全体の健全性チェック、統計情報表示、トラブルシューティング支援
"""

import sys
import os
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lab_instruments


def print_header(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title):
    """Print subsection header"""
    print(f"\n--- {title} ---")


def diagnose_system():
    """Complete system diagnosis"""
    print_header("LAB INSTRUMENTS SYSTEM DIAGNOSTICS")
    
    try:
        diagnosis = lab_instruments.diagnose_system()
        
        print(f"Diagnosis Time: {diagnosis['timestamp']}")
        
        # Registry Status
        print_subsection("Registry Status")
        registry_stats = diagnosis['registry_status']
        if registry_stats:
            print(f"Discovery Status: {'✓' if registry_stats.get('successful', 0) > 0 else '✗'}")
            print(f"Plugins Directory: {registry_stats.get('plugins_dir', 'N/A')}")
            print(f"Attempted: {registry_stats.get('attempted', 0)}")
            print(f"Successful: {registry_stats.get('successful', 0)}")
            print(f"Failed: {registry_stats.get('failed', 0)}")
            
            if registry_stats.get('errors'):
                print("Errors:")
                for error in registry_stats['errors']:
                    print(f"  - {error}")
        
        # Device Status
        print_subsection("Device Status")
        devices = diagnosis['devices']
        if devices:
            for device_name, device_data in devices.items():
                status = "✓" if device_data['valid'] else "✗"
                print(f"{status} {device_name}")
                
                if not device_data['valid']:
                    for error in device_data['errors']:
                        print(f"    Error: {error}")
                
                if device_data['info']:
                    info = device_data['info']
                    print(f"    Class: {info.get('class_name', 'N/A')}")
                    print(f"    Module: {info.get('module', 'N/A')}")
                    print(f"    Config: {'✓' if info.get('has_config') else '✗'}")
        else:
            print("No devices registered")
        
        # Stub Status
        print_subsection("Type Stub Status")
        stub_status = diagnosis['stub_status']
        print(f"Stub File Exists: {'✓' if stub_status['exists'] else '✗'}")
        
        generation_stats = stub_status.get('generation_stats', {})
        if generation_stats:
            print(f"Last Generation: {generation_stats.get('generated_at', 'N/A')}")
            print(f"Generation Success: {'✓' if generation_stats.get('success') else '✗'}")
            print(f"Devices Count: {generation_stats.get('devices_count', 0)}")
        
        # Connection Statistics
        print_subsection("Connection Statistics")
        conn_stats = diagnosis['connection_stats']
        print(f"Total Connections: {conn_stats.get('total_connections', 0)}")
        print(f"Successful: {conn_stats.get('successful_connections', 0)}")
        print(f"Failed: {conn_stats.get('failed_connections', 0)}")
        print(f"Currently Active: {conn_stats.get('active_connections', 0)}")
        print(f"Pool Size: {conn_stats.get('pool_size', 0)}")
        
        # Issues Summary
        issues = diagnosis.get('issues', [])
        if issues:
            print_subsection("Issues Found")
            for issue in issues:
                print(f"⚠️  {issue}")
        else:
            print_subsection("Issues Found")
            print("✓ No issues detected")
            
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        return False
    
    return len(issues) == 0


def list_devices_detailed():
    """List all devices with detailed information"""
    print_header("REGISTERED DEVICES")
    
    devices = lab_instruments.list_devices()
    if not devices:
        print("No devices registered")
        return
    
    for device_name in devices:
        print_subsection(f"Device: {device_name}")
        
        # Get detailed info
        info = lab_instruments.get_device_info(device_name)
        if info:
            print(f"Class: {info['class_name']}")
            print(f"Module: {info['module']}")
            print(f"Discovered: {info['discovered_at']}")
            print(f"Config File: {'✓' if info['has_config'] else '✗'}")
            
            # Validation
            is_valid, errors = lab_instruments.validate_device(device_name)
            print(f"Configuration: {'✓ Valid' if is_valid else '✗ Invalid'}")
            if errors:
                for error in errors:
                    print(f"  - {error}")
            
            # Methods
            methods = info.get('methods', [])
            if methods:
                print(f"Available Methods ({len(methods)}):")
                for method in methods[:5]:  # Show first 5 methods
                    print(f"  - {method['name']}: {method['doc'][:50]}...")
                if len(methods) > 5:
                    print(f"  ... and {len(methods) - 5} more")


def show_connection_stats():
    """Show detailed connection statistics"""
    print_header("CONNECTION STATISTICS")
    
    stats = lab_instruments.get_connection_stats()
    
    print(f"Total Connections Attempted: {stats['total_connections']}")
    print(f"Successful Connections: {stats['successful_connections']}")
    print(f"Failed Connections: {stats['failed_connections']}")
    print(f"Currently Active: {stats['active_connections']}")
    print(f"Connection Pool Size: {stats['pool_size']}")
    
    if stats['total_connections'] > 0:
        success_rate = (stats['successful_connections'] / stats['total_connections']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    # Recent connection history
    history = stats.get('connection_history', [])
    if history:
        print_subsection("Recent Connections")
        for conn in history[-5:]:  # Show last 5 connections
            status = "✓" if conn['success'] else "✗"
            device = conn.get('device', 'raw')
            duration = conn.get('duration', 0)
            print(f"{status} {device} ({duration:.3f}s)")
            if not conn['success'] and conn.get('error'):
                print(f"    Error: {conn['error']}")


def test_device_connection(device_name):
    """Test connection to a specific device"""
    print_header(f"TESTING DEVICE: {device_name}")
    
    # Check if device is registered
    if device_name not in lab_instruments.list_devices():
        print(f"❌ Device '{device_name}' not found in registry")
        print(f"Available devices: {lab_instruments.list_devices()}")
        return False
    
    # Validate configuration
    print("Validating configuration...")
    is_valid, errors = lab_instruments.validate_device(device_name)
    if not is_valid:
        print(f"❌ Configuration invalid:")
        for error in errors:
            print(f"  - {error}")
        return False
    print("✓ Configuration valid")
    
    # Test connection
    print("Testing connection...")
    try:
        with lab_instruments.connect(dev=device_name) as device:
            print("✓ Connection successful")
            
            # Try to get device ID
            try:
                device_id = device.idn()
                print(f"✓ Device ID: {device_id}")
            except Exception as e:
                print(f"⚠️  Could not get device ID: {e}")
            
            # Show available methods
            methods = [m for m in dir(device) if not m.startswith('_') and callable(getattr(device, m))]
            print(f"✓ Available methods: {len(methods)}")
            for method in methods[:10]:  # Show first 10
                print(f"  - {method}")
            if len(methods) > 10:
                print(f"  ... and {len(methods) - 10} more")
                
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def refresh_system():
    """Refresh plugins and regenerate stubs"""
    print_header("REFRESHING SYSTEM")
    
    print("Refreshing plugins...")
    try:
        result = lab_instruments.refresh_plugins()
        
        print(f"✓ Refresh completed")
        print(f"Old devices: {len(result['old_devices'])}")
        print(f"New devices: {len(result['new_devices'])}")
        
        if result['added_devices']:
            print(f"Added devices: {', '.join(result['added_devices'])}")
        
        if result['removed_devices']:
            print(f"Removed devices: {', '.join(result['removed_devices'])}")
            
        print(f"Stub regenerated: {'✓' if result['stub_regenerated'] else '✗'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Refresh failed: {e}")
        return False


def export_diagnostics(output_file):
    """Export diagnostics to JSON file"""
    print(f"Exporting diagnostics to {output_file}...")
    
    try:
        diagnosis = lab_instruments.diagnose_system()
        
        # Add additional info
        diagnosis['export_info'] = {
            'exported_at': datetime.now().isoformat(),
            'lab_instruments_version': getattr(lab_instruments, '__version__', 'unknown'),
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        with open(output_file, 'w') as f:
            json.dump(diagnosis, f, indent=2, default=str)
        
        print(f"✓ Diagnostics exported to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Lab Instruments System Diagnostics Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/diagnostics.py                    # Full system diagnosis
  python scripts/diagnostics.py --devices          # List devices with details
  python scripts/diagnostics.py --test im3590     # Test specific device
  python scripts/diagnostics.py --refresh         # Refresh plugins and stubs
  python scripts/diagnostics.py --export diag.json # Export diagnostics
        """
    )
    
    parser.add_argument('--devices', action='store_true',
                       help='List all devices with detailed information')
    parser.add_argument('--stats', action='store_true',
                       help='Show connection statistics')
    parser.add_argument('--test', metavar='DEVICE',
                       help='Test connection to specific device')
    parser.add_argument('--refresh', action='store_true',
                       help='Refresh plugins and regenerate stubs')
    parser.add_argument('--export', metavar='FILE',
                       help='Export diagnostics to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Configure logging if verbose
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    success = True
    
    try:
        if args.devices:
            list_devices_detailed()
        elif args.stats:
            show_connection_stats()
        elif args.test:
            success = test_device_connection(args.test)
        elif args.refresh:
            success = refresh_system()
        elif args.export:
            success = export_diagnostics(args.export)
        else:
            # Default: full system diagnosis
            success = diagnose_system()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()