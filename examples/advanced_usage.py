#!/usr/bin/env python3
"""
Advanced usage examples for lab-instruments package.
Shows configuration override, batch operations, and error handling.
"""

import lab_instruments
import time
from contextlib import contextmanager

@contextmanager
def safe_device_connection(device_name, **overrides):
    """Safe device connection with proper error handling"""
    device = None
    try:
        device = lab_instruments.connect(dev=device_name, **overrides)
        print(f"Successfully connected to {device_name}")
        yield device
    except Exception as e:
        print(f"Failed to connect to {device_name}: {e}")
        yield None
    finally:
        if device:
            device.close()
            print(f"Disconnected from {device_name}")

def example_config_override():
    """Example of overriding default configuration"""
    print("\n--- Example: Configuration Override ---")
    
    # Override default config parameters
    with safe_device_connection("im3590", 
                               method="serial", 
                               port="/dev/ttyUSB1", 
                               baudrate=115200) as lcr:
        if lcr:
            print(f"Device ID: {lcr.idn()}")
            print("Using custom serial parameters")

def example_batch_measurements():
    """Example of batch measurement operations"""
    print("\n--- Example: Batch Measurements ---")
    
    frequencies = [100, 1000, 10000, 100000]  # Hz
    
    with safe_device_connection("im3590") as lcr:
        if lcr:
            print("Performing frequency sweep measurements...")
            results = []
            
            for freq in frequencies:
                lcr.set_freq(freq)
                time.sleep(0.1)  # Allow settling time
                measurement = lcr.measure()
                results.append((freq, measurement))
                print(f"  {freq} Hz: {measurement}")
            
            print(f"Completed {len(results)} measurements")

def example_multiple_devices():
    """Example using multiple devices simultaneously"""
    print("\n--- Example: Multiple Device Operation ---")
    
    # Connect to multiple devices
    devices = {}
    
    try:
        # Connect to LCR meter
        if "im3590" in lab_instruments.list_devices():
            devices["lcr"] = lab_instruments.connect(dev="im3590")
            print("LCR meter connected")
        
        # Connect to electronic load
        if "plz164w" in lab_instruments.list_devices():
            devices["load"] = lab_instruments.connect(dev="plz164w")
            print("Electronic load connected")
        
        # Synchronized operation
        if "lcr" in devices and "load" in devices:
            print("Performing synchronized test...")
            
            # Set load current
            devices["load"].load_on()
            devices["load"].set_current(0.1)  # 100mA
            
            time.sleep(1)  # Allow settling
            
            # Measure with LCR
            devices["lcr"].set_freq(1000)
            measurement = devices["lcr"].measure()
            print(f"Measurement under load: {measurement}")
            
            # Turn off load
            devices["load"].load_off()
            print("Test completed")
    
    except Exception as e:
        print(f"Multi-device operation failed: {e}")
    
    finally:
        # Clean up connections
        for name, device in devices.items():
            try:
                device.close()
                print(f"{name} disconnected")
            except:
                pass

def example_custom_command_sequence():
    """Example of custom SCPI command sequences"""
    print("\n--- Example: Custom Command Sequences ---")
    
    with safe_device_connection("im3590") as lcr:
        if lcr:
            # Custom initialization sequence
            commands = [
                "*RST",           # Reset device
                "*CLS",           # Clear status
                "FUNC:IMP Z",     # Set impedance measurement mode  
                "FREQ 1000",      # Set frequency to 1kHz
                "VOLT 1",         # Set voltage level to 1V
                "TRIG:SOUR BUS",  # Set trigger source to bus
            ]
            
            print("Executing custom initialization sequence...")
            for cmd in commands:
                lcr.send(cmd)
                time.sleep(0.01)  # Small delay between commands
            
            print("Initialization complete")
            
            # Query device state
            state_queries = [
                ("Function", "FUNC:IMP?"),
                ("Frequency", "FREQ?"),
                ("Voltage", "VOLT?"),
                ("Trigger Source", "TRIG:SOUR?")
            ]
            
            print("Device state:")
            for name, query in state_queries:
                try:
                    response = lcr.query(query)
                    print(f"  {name}: {response}")
                except Exception as e:
                    print(f"  {name}: Query failed - {e}")

def example_error_handling():
    """Example of comprehensive error handling"""
    print("\n--- Example: Error Handling ---")
    
    # Test with non-existent device
    try:
        with lab_instruments.connect(dev="nonexistent") as device:
            pass
    except ValueError as e:
        print(f"Expected error for non-existent device: {e}")
    
    # Test with invalid method
    try:
        with lab_instruments.connect(method="invalid_method") as conn:
            pass
    except ValueError as e:
        print(f"Expected error for invalid method: {e}")
    
    # Test connection timeout handling
    try:
        with lab_instruments.connect(method="serial", 
                                   port="/dev/nonexistent", 
                                   timeout=0.1) as conn:
            pass
    except Exception as e:
        print(f"Expected connection error: {type(e).__name__}")

def main():
    """Main demonstration function"""
    print("=== Advanced Lab Instruments Examples ===")
    
    devices = lab_instruments.list_devices()
    print(f"Available devices: {devices}")
    
    if not devices:
        print("No devices available for advanced examples")
        return
    
    # Run advanced examples
    example_config_override()
    example_batch_measurements()
    example_multiple_devices()
    example_custom_command_sequence()
    example_error_handling()
    
    print("\n=== Advanced Examples Complete ===")

if __name__ == "__main__":
    main()