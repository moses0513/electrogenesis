import argparse
import sys
import serial

#!/usr/bin/env python3
# Connect to a COM port and print "success" on a successful open.

def main():
    parser = argparse.ArgumentParser(description="Open a serial COM port and print success.")
    parser.add_argument("-p", "--port", default="COM6",
                        help="Serial port name (e.g. COM3 on Windows or /dev/ttyUSB0 on Linux)")
    parser.add_argument("-b", "--baud", type=int, default=9600, help="Baud rate (default: 9600)")
    args = parser.parse_args()

    try:
        with serial.Serial(args.port, args.baud, timeout=1) as ser:
            if ser.is_open:
                print("success")
                return 0
            else:
                print("failed to open port", file=sys.stderr)
                return 1
    except serial.SerialException as e:
        print(f"error opening port: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())