# mcu_side.py
import time

# -----------------------------
# PLATFORM DETECTION
# -----------------------------
try:
    import RPi.GPIO as GPIO
    ON_PI = True
except ImportError:
    GPIO = None
    ON_PI = False

# -----------------------------
# GPIO PIN DEFINITIONS
# CHANGE THESE TO MATCH WIRING
# -----------------------------
AXES = {
    'X': {'STEP': 17, 'DIR': 16},
    'Y': {'STEP': 27, 'DIR': 26},
    'Z': {'STEP': 22, 'DIR': 21},
}

STEP_DELAY = 0.0005  # seconds

# -----------------------------
# GPIO SETUP (Pi only)
# -----------------------------
if ON_PI:
    GPIO.setmode(GPIO.BCM)
    for axis in AXES.values():
        GPIO.setup(axis['STEP'], GPIO.OUT)
        GPIO.setup(axis['DIR'], GPIO.OUT)

# -----------------------------
# MOTOR CONTROL
# -----------------------------
def move_motor(axis, direction, steps):
    """
    axis: 'X', 'Y', or 'Z'
    direction: '+' or '-'
    steps: int
    """

    if not ON_PI:
        print(f"[SIM] {axis}{direction} moving {steps} steps")
        return

    # Set direction
    GPIO.output(AXES[axis]['DIR'], GPIO.HIGH if direction == '+' else GPIO.LOW)

    step_pin = AXES[axis]['STEP']

    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(STEP_DELAY)

def cleanup():
    if ON_PI:
        GPIO.cleanup()
