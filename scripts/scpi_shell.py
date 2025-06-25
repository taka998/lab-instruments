import argparse
import lab_instruments
from lab_instruments.core.scpi.common_scpi import CommonSCPI

def main():
    parser = argparse.ArgumentParser(description="SCPI Shell CLI")
    parser.add_argument("--dev", type=str, help="Device name (uses plugins/{dev}/config.json)")
    parser.add_argument("--method", type=str, help="Connection method (serial/socket/visa)")
    parser.add_argument("--plugins-dir", type=str, default="plugins", help="Plugins directory")
    parser.add_argument("--port", type=str, help="Serial port or socket port")
    parser.add_argument("--baudrate", type=int, help="Baudrate")
    parser.add_argument("--host", type=str, help="Socket host")
    parser.add_argument("--timeout", type=float, help="Timeout in seconds")
    parser.add_argument("--terminator", type=str, help="Terminator (CR, LF, CRLF, etc.)")
    args = parser.parse_args()

    kwargs = {}
    for k in ["port", "baudrate", "host", "timeout", "terminator"]:
        v = getattr(args, k)
        if v is not None:
            kwargs[k] = v

    try:
        scpi = lab_instruments.connect(
            dev=args.dev,
            method=args.method,
            plugins_dir=args.plugins_dir,
            **kwargs
        )
    except Exception as e:
        print(f"Connection error: {e}")
        return

    if not isinstance(scpi, CommonSCPI):
        scpi = CommonSCPI(scpi)

    print("Welcome to the SCPI shell. Type 'exit' or 'quit' to leave.")
    while True:
        try:
            cmd = input("SCPI> ").strip()
            if cmd.lower() in ("exit", "quit"):
                break
            if not cmd:
                continue
            if cmd.endswith("?"):
                res = scpi.query(cmd)
                print(res)
            else:
                scpi.send(cmd)
                print("OK")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
