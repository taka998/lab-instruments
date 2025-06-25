#!/usr/bin/env python3
"""
Test script for lab_instruments package
"""
import sys
from pathlib import Path

# Add the current directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent))

def test_package_import():
    """Test basic package imports"""
    print("Testing package imports...")
    try:
        print("✓ lab_instruments imported successfully")
        
        from lab_instruments import list_devices
        print("✓ Main functions imported successfully")
        
        devices = list_devices()
        print(f"✓ Available devices: {devices}")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_registry():
    """Test device registry functionality"""
    print("\nTesting device registry...")
    try:
        from lab_instruments.registry import registry
        
        devices = registry.list_devices()
        print(f"✓ Registry devices: {devices}")
        
        for device in devices:
            device_info = registry.get_device_info(device)
            if device_info:
                print(f"✓ Device {device}: {device_info.device_class.__name__}")
                
                # Test typed connect function
                typed_connect = registry.get_typed_connect(device)
                if typed_connect:
                    print(f"✓ Typed connect function available for {device}")
        
        return True
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
        return False

def test_stub_generation():
    """Test stub file generation"""
    print("\nTesting stub generation...")
    try:
        from lab_instruments.stub_manager import stub_manager
        
        # Force stub generation
        stub_manager.generate_stub()
        
        if stub_manager.stub_file.exists():
            print("✓ Stub file generated successfully")
            
            # Show first few lines of stub file
            content = stub_manager.stub_file.read_text()
            lines = content.split('\n')[:10]
            print("✓ Stub file preview:")
            for line in lines:
                print(f"    {line}")
        else:
            print("✗ Stub file not found")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Stub generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Lab Instruments Package Test")
    print("=" * 50)
    
    tests = [
        test_package_import,
        test_registry,
        test_stub_generation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
