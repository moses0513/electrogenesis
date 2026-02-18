import os
import sys
import time

try:
    import RPi.GPIO as GPIO
except Exception as exc:  # RPi.GPIO not available or not supported
    GPIO = None
    _GPIO_IMPORT_ERROR = exc


def _is_raspberry_pi() -> bool:
    # Fast, dependency-free checks.
    model_paths = (
        "/proc/device-tree/model",
        "/sys/firmware/devicetree/base/model",
    )
    for path in model_paths:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                if "raspberry pi" in f.read().lower():
                    return True
        except FileNotFoundError:
            pass

    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
            return "raspberry pi" in f.read().lower()
    except FileNotFoundError:
        return Falsewire an LED (or your device) to BCM pin 17.



# Set up GPIO mode
if GPIO is None:
    print(
        "RPi.GPIO is not available. Install it on a Raspberry Pi, "
        "or run on Pi hardware to access GPIO.\n"
        f"Details: {_GPIO_IMPORT_ERROR}",
        file=sys.stderr,
    )
    sys.exit(1)

if not _is_raspberry_pi():
    print(
        "GPIO access requires Raspberry Pi hardware. "
        "This script should be run on a Raspberry Pi (BCM GPIO).",
        file=sys.stderr,
    )
    sys.exit(1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

try:
    while True:
        GPIO.output(17, GPIO.HIGH)  # Turn LED on
        time.sleep(1)
        GPIO.output(17, GPIO.LOW)   # Turn LED off
        time.sleep(1)
finally:
    GPIO.cleanup()  # Clean up GPIO on exit
