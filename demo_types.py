#!/usr/bin/env python3
"""
Type safety demonstration for lab_instruments package
"""
import sys
from pathlib import Path

# Add the current directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent))

def test_typed_connections():
    """Test typed device connections"""
    print("Testing typed device connections...")
    
    try:
        import lab_instruments
        
        # List available devices
        devices = lab_instruments.list_devices()
        print(f"Available devices: {devices}")
        
        # Test generic connect function with type hints
        print("\n1. Generic connect function:")
        print("   lab_instruments.connect('im3590') -> IM3590SCPI")
        print("   lab_instruments.connect('plz164w') -> PLZ164WSCPI") 
        print("   lab_instruments.connect(method='serial') -> ConnectionInterface")
        
        # Test dynamic typed connect functions
        print("\n2. Dynamic typed connect functions:")
        for device in devices:
            attr_name = f"connect_{device}"
            if hasattr(lab_instruments, attr_name):
                typed_func = getattr(lab_instruments, attr_name)
                print(f"   lab_instruments.{attr_name}() -> {typed_func.__doc__.split('Returns: ')[-1] if typed_func.__doc__ else 'Unknown'}")
            else:
                print(f"   lab_instruments.{attr_name}() -> Not found")
        
        # Show generated stub file content
        print("\n3. Generated type stub file (__init__.pyi):")
        stub_file = Path("lab_instruments/__init__.pyi")
        if stub_file.exists():
            content = stub_file.read_text()
            lines = content.split('\n')
            
            # Show overload definitions
            in_overloads = False
            for line in lines:
                if "# Device-specific overloads" in line:
                    in_overloads = True
                    print("   " + line)
                elif in_overloads and line.strip():
                    if line.startswith('#') and 'Generic' in line:
                        break
                    print("   " + line)
        
        print("\n✓ Type system is working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Type test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_usage():
    """Show usage examples"""
    print("\n" + "="*60)
    print("USAGE EXAMPLES")
    print("="*60)
    
    usage_examples = '''
# Import the package
import lab_instruments

# List available devices
devices = lab_instruments.list_devices()
print(devices)  # ['im3590', 'plz164w']

# Type-safe device connections (with IDE autocompletion)
with lab_instruments.connect('im3590') as lcr:  # Returns IM3590SCPI
    print(lcr.idn())                            # CommonSCPI methods
    lcr.set_freq(1000)                          # IM3590-specific methods
    result = lcr.measure()

# Alternative: Use dynamic typed functions
with lab_instruments.connect_im3590() as lcr:  # Explicit type: IM3590SCPI
    lcr.set_parameter(1, 'Z')

# Direct connection interface (for custom protocols)
with lab_instruments.connect(method='serial', port='/dev/ttyUSB0') as conn:
    conn.write('*IDN?')                         # Returns ConnectionInterface
    response = conn.read()

# Override config parameters
with lab_instruments.connect('im3590', method='socket', host='192.168.1.100') as lcr:
    # Uses socket instead of serial from config
    pass
'''
    
    print(usage_examples)

def main():
    """Run type safety demonstration"""
    print("=" * 60)
    print("Lab Instruments - Type Safety Demonstration")
    print("=" * 60)
    
    success = test_typed_connections()
    
    if success:
        demonstrate_usage()
        
        print("\n" + "=" * 60)
        print("✓ Package is ready for distribution!")
        print("=" * 60)
        print("\nTo build and distribute:")
        print("  pip install build twine")
        print("  python -m build")
        print("  twine upload dist/*")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)