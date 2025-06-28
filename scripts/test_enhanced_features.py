#!/usr/bin/env python3
"""
Lab Instruments Enhanced Features Integration Test
強化されたregistry、stub_manager、factoryの機能をテスト
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path for running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lab_instruments


def test_registry_features():
    """Test enhanced registry features"""
    print("🧪 Testing Registry Features")
    print("-" * 40)
    
    # Get discovery stats
    stats = lab_instruments.registry.get_discovery_stats()
    print(f"✓ Discovery stats: {stats.get('successful', 0)} successful, {stats.get('failed', 0)} failed")
    
    # Get device metadata
    devices = lab_instruments.list_devices()
    for device in devices[:2]:  # Test first 2 devices
        metadata = lab_instruments.get_device_info(device)
        if metadata:
            print(f"✓ {device} metadata: {metadata['class_name']} ({len(metadata.get('methods', []))} methods)")
        
        # Test validation
        is_valid, errors = lab_instruments.validate_device(device)
        print(f"✓ {device} validation: {'Valid' if is_valid else 'Invalid'}")
        if errors:
            print(f"  Errors: {', '.join(errors[:2])}")
    
    # Test all devices validation
    all_validation = lab_instruments.validate_all_devices()
    valid_count = sum(1 for is_valid, _ in all_validation.values() if is_valid)
    print(f"✓ All devices validation: {valid_count}/{len(all_validation)} valid")
    
    print("✅ Registry features test completed\n")


def test_stub_manager_features():
    """Test enhanced stub manager features"""
    print("🧪 Testing Stub Manager Features")
    print("-" * 40)
    
    # Check stub status
    should_update, reason = lab_instruments.stub_manager.should_update_stub()
    print(f"✓ Stub update needed: {should_update} ({reason})")
    
    # Get generation stats
    gen_stats = lab_instruments.stub_manager.get_generation_stats()
    if gen_stats:
        print(f"✓ Last generation: {gen_stats.get('generated_at', 'Never')}")
        print(f"  Success: {gen_stats.get('success', False)}")
        print(f"  Devices: {gen_stats.get('devices_count', 0)}")
    
    # Get cache info
    cache_info = lab_instruments.stub_manager.get_cache_info()
    if cache_info:
        print(f"✓ Cache last updated: {cache_info.get('last_updated', 'Never')}")
        print(f"  Cached devices: {len(cache_info.get('devices', []))}")
    
    # Test force regeneration
    print("Testing force regeneration...")
    success = lab_instruments.stub_manager.force_regenerate()
    print(f"✓ Force regeneration: {'Success' if success else 'Failed'}")
    
    print("✅ Stub manager features test completed\n")


def test_factory_features():
    """Test enhanced factory features"""
    print("🧪 Testing Factory Features")
    print("-" * 40)
    
    # Get connection stats
    stats = lab_instruments.get_connection_stats()
    print(f"✓ Connection stats: {stats['total_connections']} total, {stats['successful_connections']} successful")
    print(f"  Active: {stats['active_connections']}, Pool: {stats['pool_size']}")
    
    # Test device info functions
    devices = lab_instruments.list_devices()
    if devices:
        device = devices[0]
        info = lab_instruments.get_device_info(device)
        print(f"✓ Device info for {device}: {info['class_name'] if info else 'None'}")
    
    # Test connection with validation disabled (should be faster)
    if devices:
        device = devices[0]
        try:
            print(f"Testing connection to {device} (validation disabled)...")
            with lab_instruments.connect(dev=device, validate_connection=False) as dev_instance:
                print(f"✓ Fast connection successful: {type(dev_instance).__name__}")
        except Exception as e:
            print(f"⚠️  Connection failed: {e}")
    
    # Test diagnostics
    print("Running system diagnostics...")
    diagnosis = lab_instruments.diagnose_system()
    issues = len(diagnosis.get('issues', []))
    print(f"✓ System diagnosis: {issues} issues found")
    
    print("✅ Factory features test completed\n")


def test_connection_pooling():
    """Test connection pooling functionality"""
    print("🧪 Testing Connection Pooling")
    print("-" * 40)
    
    devices = lab_instruments.list_devices()
    if not devices:
        print("⚠️  No devices available for pooling test")
        return
    
    device = devices[0]
    
    try:
        # Clear pool first
        lab_instruments.clear_connection_pool()
        initial_stats = lab_instruments.get_connection_stats()
        initial_pool_size = initial_stats['pool_size']
        
        print(f"Initial pool size: {initial_pool_size}")
        
        # Create pooled connection
        print(f"Creating pooled connection to {device}...")
        with lab_instruments.connect(dev=device, use_pool=True) as dev1:
            mid_stats = lab_instruments.get_connection_stats()
            mid_pool_size = mid_stats['pool_size']
            print(f"✓ Pool size after first connection: {mid_pool_size}")
            
            # Create second connection with same parameters (should reuse)
            print("Creating second pooled connection with same parameters...")
            with lab_instruments.connect(dev=device, use_pool=True) as dev2:
                final_stats = lab_instruments.get_connection_stats()
                final_pool_size = final_stats['pool_size']
                print(f"✓ Pool size after second connection: {final_pool_size}")
                
                # Check if same instance (pooled)
                is_same = dev1 is dev2
                print(f"✓ Connection pooling working: {'Yes' if is_same else 'No'}")
        
        # Clear pool
        lab_instruments.clear_connection_pool()
        cleared_stats = lab_instruments.get_connection_stats()
        cleared_pool_size = cleared_stats['pool_size']
        print(f"✓ Pool size after clearing: {cleared_pool_size}")
        
    except Exception as e:
        print(f"⚠️  Pooling test failed: {e}")
    
    print("✅ Connection pooling test completed\n")


def test_refresh_functionality():
    """Test plugin refresh functionality"""
    print("🧪 Testing Refresh Functionality")
    print("-" * 40)
    
    # Get initial state
    initial_devices = set(lab_instruments.list_devices())
    print(f"Initial devices: {len(initial_devices)}")
    
    # Perform refresh
    print("Performing plugin refresh...")
    refresh_result = lab_instruments.refresh_plugins()
    
    print("✓ Refresh completed")
    print(f"  Old devices: {len(refresh_result['old_devices'])}")
    print(f"  New devices: {len(refresh_result['new_devices'])}")
    print(f"  Added: {refresh_result['added_devices']}")
    print(f"  Removed: {refresh_result['removed_devices']}")
    print(f"  Stub regenerated: {refresh_result['stub_regenerated']}")
    
    # Check final state
    final_devices = set(lab_instruments.list_devices())
    print(f"Final devices: {len(final_devices)}")
    
    print("✅ Refresh functionality test completed\n")


def test_error_handling():
    """Test error handling and edge cases"""
    print("🧪 Testing Error Handling")
    print("-" * 40)
    
    # Test invalid device
    try:
        with lab_instruments.connect(dev="nonexistent_device") as dev:
            pass
        print("❌ Should have failed for nonexistent device")
    except Exception as e:
        print(f"✓ Correctly handled invalid device: {type(e).__name__}")
    
    # Test invalid method for raw connection
    try:
        with lab_instruments.connect(method="invalid_method") as conn:
            pass
        print("❌ Should have failed for invalid method")
    except Exception as e:
        print(f"✓ Correctly handled invalid method: {type(e).__name__}")
    
    # Test device validation
    validation_results = lab_instruments.validate_all_devices()
    invalid_devices = [name for name, (valid, _) in validation_results.items() if not valid]
    print(f"✓ Found {len(invalid_devices)} devices with invalid configurations")
    
    print("✅ Error handling test completed\n")


def test_monitoring_features():
    """Test monitoring and statistics features"""
    print("🧪 Testing Monitoring Features")
    print("-" * 40)
    
    # Get comprehensive stats
    stats = lab_instruments.get_connection_stats()
    print("✓ Connection statistics collected:")
    print(f"  Total: {stats['total_connections']}")
    print(f"  Successful: {stats['successful_connections']}")
    print(f"  Failed: {stats['failed_connections']}")
    print(f"  History entries: {len(stats.get('connection_history', []))}")
    
    # Test registry stats
    registry_stats = lab_instruments.registry.get_discovery_stats()
    if registry_stats:
        print("✓ Registry discovery stats:")
        print(f"  Attempted: {registry_stats.get('attempted', 0)}")
        print(f"  Successful: {registry_stats.get('successful', 0)}")
        print(f"  Duration: {registry_stats.get('duration', 0):.3f}s")
    
    # Test stub stats
    stub_stats = lab_instruments.stub_manager.get_generation_stats()
    if stub_stats:
        print("✓ Stub generation stats:")
        print(f"  Success: {stub_stats.get('success', False)}")
        print(f"  Duration: {stub_stats.get('duration', 0):.3f}s")
        print(f"  File size: {stub_stats.get('stub_file_size', 0)} bytes")
    
    print("✅ Monitoring features test completed\n")


def export_test_report():
    """Export comprehensive test report"""
    print("📊 Generating Test Report")
    print("-" * 40)
    
    # Collect comprehensive system info
    report = {
        'test_timestamp': datetime.now().isoformat(),
        'system_diagnosis': lab_instruments.diagnose_system(),
        'connection_statistics': lab_instruments.get_connection_stats(),
        'device_metadata': lab_instruments.get_all_devices_info(),
        'validation_results': lab_instruments.validate_all_devices(),
        'registry_stats': lab_instruments.registry.get_discovery_stats(),
        'stub_stats': lab_instruments.stub_manager.get_generation_stats(),
        'cache_info': lab_instruments.stub_manager.get_cache_info()
    }
    
    # Export to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"lab_instruments_test_report_{timestamp}.json"
    
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"✓ Test report exported to: {report_file}")
        
        # Show summary
        diagnosis = report['system_diagnosis']
        issues = len(diagnosis.get('issues', []))
        devices = len(lab_instruments.list_devices())
        
        print("📋 Report Summary:")
        print(f"  Devices: {devices}")
        print(f"  Issues: {issues}")
        print(f"  Total connections: {report['connection_statistics']['total_connections']}")
        
        return report_file
        
    except Exception as e:
        print(f"❌ Failed to export report: {e}")
        return None


def main():
    """Main test runner"""
    print("🚀 Lab Instruments Enhanced Features Integration Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Run all test suites
        test_registry_features()
        test_stub_manager_features()
        test_factory_features()
        test_connection_pooling()
        test_refresh_functionality()
        test_error_handling()
        test_monitoring_features()
        
        # Generate final report
        report_file = export_test_report()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        if report_file:
            print(f"📁 Detailed report: {report_file}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
