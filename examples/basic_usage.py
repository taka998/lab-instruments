#!/usr/bin/env python3
"""
Basic usage examples for lab-instruments package.
Demonstrates the new factory architecture and registry system.
"""

import lab_instruments

def list_available_devices():
    """Show all available devices in the registry"""
    print("Available devices:")
    devices = lab_instruments.list_devices()
    for device in devices:
        print(f"  - {device}")
    return devices

def example_typed_connection():
    """Example using typed device connections"""
    print("\n--- Example: Typed Device Connection ---")
    
    # This will provide proper type hints and intellisense
    try:
        with lab_instruments.connect(dev="im3590") as lcr:
            print(f"Connected to: {lcr.idn()}")
            lcr.set_freq(1000)
            print(f"Set frequency to: {lcr.get_freq()}")
            measurement = lcr.measure()
            print(f"Measurement: {measurement}")
    except Exception as e:
        print(f"Failed to connect to im3590: {e}")

def example_raw_connection():
    """Example using raw connection interface"""
    print("\n--- Example: Raw Connection Interface ---")
    
    try:
        # Returns a ConnectionInterface without device wrapper
        with lab_instruments.connect(method="serial", port="/dev/ttyUSB0", baudrate=9600) as conn:
            conn.write("*IDN?")
            response = conn.read()
            print(f"Device ID: {response}")
    except Exception as e:
        print(f"Failed to create raw connection: {e}")

def example_dynamic_typed_connect():
    """Example using dynamically generated typed connect functions"""
    print("\n--- Example: Dynamic Typed Connect Functions ---")
    
    try:
        # These functions are auto-generated based on registered devices
        # lab_instruments.connect_im3590() -> IM3590SCPI
        # lab_instruments.connect_plz164w() -> PLZ164WSCPI
        
        if hasattr(lab_instruments, 'connect_im3590'):
            with lab_instruments.connect_im3590() as lcr:
                print(f"IM3590 via typed connect: {lcr.idn()}")
        
        if hasattr(lab_instruments, 'connect_plz164w'):
            with lab_instruments.connect_plz164w() as load:
                print(f"PLZ164W via typed connect: {load.idn()}")
                load.load_on()
                print("Load turned ON")
                load.load_off()
                print("Load turned OFF")
                
    except Exception as e:
        print(f"Dynamic typed connect failed: {e}")

def main():
    """Main demonstration function"""
    print("=== Lab Instruments Package Examples ===")
    
    # List available devices
    devices = list_available_devices()
    
    if not devices:
        print("\nNo devices found. Make sure plugins are properly installed.")
        return
    
    # Show different connection methods
    example_typed_connection()
    example_raw_connection() 
    example_dynamic_typed_connect()
    
    print("\n=== Examples Complete ===")

if __name__ == "__main__":
    main()