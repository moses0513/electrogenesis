from machine import Pin, PWM
import utime4
#

# Assign pins
pwma = PWM(Pin(0))
AIN1 = Pin(1, Pin.OUT)
AIN2 = Pin(2, Pin.OUT)

pwmb = PWM(Pin(3))
BIN1 = Pin(4, Pin.OUT)
BIN2 = Pin(5, Pin.OUT)

stby = Pin(15, Pin.OUT)
stby.value(1)  # enable driveryy

# Stepper sequence for full-step driving (bipolar)
sequence = [
    [1, 0, 1, 0],  # Coil A+, B+
    [0, 1, 1, 0],  # Coil A-, B+
    [0, 1, 0, 1],  # Coil A-, B-
    [1, 0, 0, 1],  # Coil A+, B-
]

# Function to set coil states
def set_coils(state):
    AIN1.value(state[0])
    AIN2.value(state[1])
    BIN1.value(state[2])
    BIN2.value(state[3])

# Rotate stepper
def step_motor(steps, delay=2):
    for i in range(steps):
        for step in sequence:
            set_coils(step)
            utime.sleep_ms(delay)

# Example: rotate 100 steps forward
step_motor(100, delay=5)

# Stop: turn all coils off
set_coils([0,0,0,0])