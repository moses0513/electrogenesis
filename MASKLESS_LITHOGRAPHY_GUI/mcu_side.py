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
    'X': {'STEP': 23, 'DIR': 24},
    'Y': {'STEP': 5, 'DIR': 6},
    'Z': {'STEP': 13, 'DIR': 19},
}

STEP_DELAY = 0.0007  # seconds (match motorContoller.py pulse timing)

# -----------------------------
# GPIO SETUP (Pi only)
# -----------------------------
if ON_PI:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for axis in AXES.values():
        GPIO.setup(axis['STEP'], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(axis['DIR'], GPIO.OUT, initial=GPIO.LOW)

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
