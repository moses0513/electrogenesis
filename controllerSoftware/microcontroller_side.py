from machine import Pin
import time
import sys

# Example pins — update for your setup
x_motor = Pin(0, Pin.OUT)
y_motor = Pin(1, Pin.OUT)
z_motor = Pin(2, Pin.OUT)

def move_motor(axis, direction, steps):
    print(f"Moving {axis} {direction} {steps} steps")
    # here you’d call your motor driver logic, e.g. step pulse loop
    # for simplicity just blink the pin
    for _ in range(steps):
        if axis == 'X': x_motor.toggle()
        elif axis == 'Y': y_motor.toggle()
        elif axis == 'Z': z_motor.toggle()
        time.sleep_us(500)

# Serial loop
while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        cmd = sys.stdin.readline().strip()
        if not cmd:
            continue
        print("Received:", cmd)
        if cmd == "STOP":
            continue
        axis = cmd[0]
        direction = cmd[1]
        steps = int(cmd[2:])
        move_motor(axis, direction, steps)
