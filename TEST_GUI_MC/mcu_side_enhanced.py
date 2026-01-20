# mcu_side.py
# Enhanced version with emergency stop support
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

# Global step delay - can be modified by GUI
STEP_DELAY = 0.0005  # seconds (default: 0.5ms)

# Emergency stop flag
E_STOP_ACTIVE = False

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
    
    global E_STOP_ACTIVE
    
    # Check for emergency stop
    if E_STOP_ACTIVE:
        print(f"[E-STOP] Movement blocked - emergency stop is active")
        return

    if not ON_PI:
        print(f"[SIM] {axis}{direction} moving {steps} steps (delay: {STEP_DELAY*1000:.2f}ms)")
        return

    # Set direction
    GPIO.output(AXES[axis]['DIR'], GPIO.HIGH if direction == '+' else GPIO.LOW)

    step_pin = AXES[axis]['STEP']

    for i in range(steps):
        # Check e-stop during movement
        if E_STOP_ACTIVE:
            print(f"[E-STOP] Movement interrupted at step {i}/{steps}")
            break
            
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(STEP_DELAY)

def emergency_stop():
    """Activate emergency stop - halts all motor operations"""
    global E_STOP_ACTIVE
    E_STOP_ACTIVE = True
    print("🚨 EMERGENCY STOP ACTIVATED 🚨")
    
    if ON_PI:
        # Set all step pins LOW to ensure motors are stopped
        for axis in AXES.values():
            GPIO.output(axis['STEP'], GPIO.LOW)
    
    print("All motor operations halted")

def reset_emergency_stop():
    """Reset emergency stop flag - allows motor operations to resume"""
    global E_STOP_ACTIVE
    E_STOP_ACTIVE = False
    print("Emergency stop reset - motor operations can resume")

def home_axis(axis):
    """
    Home a single axis (placeholder for actual homing logic)
    
    In a real implementation, this would:
    1. Move slowly in negative direction until limit switch triggered
    2. Back off slightly
    3. Return position = 0
    """
    print(f"[HOMING] {axis} axis homing sequence started")
    
    if not ON_PI:
        print(f"[SIM] {axis} axis would home to limit switch")
        return 0
    
    # TODO: Implement actual homing with limit switches
    # This is a placeholder that you'll need to customize based on your hardware
    
    # Example logic (commented out - customize for your setup):
    # 1. Move slowly toward home until limit switch triggers
    # home_direction = '-'  # Usually home in negative direction
    # while not limit_switch_triggered(axis):
    #     move_motor(axis, home_direction, 10)  # Move in small increments
    #     if E_STOP_ACTIVE:
    #         return None
    # 
    # 2. Back off slightly from limit switch
    # move_motor(axis, '+', 50)  # Back off 50 steps
    # 
    # 3. Return homed position
    # return 0
    
    print(f"[HOMING] {axis} axis homing complete")
    return 0

def cleanup():
    """Clean up GPIO resources"""
    if ON_PI:
        GPIO.cleanup()
        print("GPIO cleanup complete")
