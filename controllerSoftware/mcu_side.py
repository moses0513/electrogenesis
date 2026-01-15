# mcu_side.py
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Example GPIO pins (change to match wiring)
X_PIN = 17
Y_PIN = 27
Z_PIN = 22

GPIO.setup(X_PIN, GPIO.OUT)
GPIO.setup(Y_PIN, GPIO.OUT)
GPIO.setup(Z_PIN, GPIO.OUT)

STEP_DELAY = 0.0005  # 500 µs

AXIS_PINS = {
    'X': X_PIN,
    'Y': Y_PIN,
    'Z': Z_PIN
}

def move_motor(axis, steps):
    pin = AXIS_PINS[axis]
    for _ in range(steps):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(STEP_DELAY)

def cleanup():
    GPIO.cleanup()
