import pyvisa

def main():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    if resources:
        print("Available VISA addresses:")
        for addr in resources:
            print(addr)
    else:
        print("No VISA addresses found.")

if __name__ == "__main__":
    main()
