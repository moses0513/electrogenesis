import threading
import time
import tkinter as tk
from tkinter import ttk

import RPi.GPIO as GPIO

# Raspberry Pi 5 (BCM mode) -> A4988 (only required Pi control wires)
#
# X axis:
# STEP: BCM23 (pin 16), DIR: BCM24 (pin 18)
#
# Y axis:
# STEP: BCM5 (pin 29), DIR: BCM6 (pin 31)
#
# Z axis:
# STEP: BCM13 (pin 33), DIR: BCM19 (pin 35)
#
# Tie these directly on each A4988 (not to Pi GPIO):
# ENABLE -> GND (always enabled)
# MS1/MS2/MS3 -> VDD (fixed 1/16 microstepping)
# RESET + SLEEP tied together -> VDD
#
# Shared power:
# GND -> A4988 GND
# 3V3 -> A4988 VDD (logic)
# External motor PSU -> VMOT/GND on each A4988

PULSE_DELAY_SEC = 0.0007

AXIS_PINS = {
    "X": {"step": 23, "dir": 24},
    "Y": {"step": 5, "dir": 6},
    "Z": {"step": 13, "dir": 19},
}

axis_busy = {"X": False, "Y": False, "Z": False}
axis_status_vars = {}
axis_step_vars = {}


def setup_gpio() -> None:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for axis, pins in AXIS_PINS.items():
        GPIO.setup(pins["step"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins["dir"], GPIO.OUT, initial=GPIO.LOW)


def update_axis_status(axis: str, message: str) -> None:
    axis_status_vars[axis].set(message)


def move_steps(axis: str, step_count: int) -> None:
    pins = AXIS_PINS[axis]
    axis_busy[axis] = True
    update_axis_status(axis, f"Moving {step_count} steps...")

    direction_state = GPIO.HIGH if step_count >= 0 else GPIO.LOW
    GPIO.output(pins["dir"], direction_state)
    time.sleep(0.001)

    for _ in range(abs(step_count)):
        GPIO.output(pins["step"], GPIO.HIGH)
        time.sleep(PULSE_DELAY_SEC)
        GPIO.output(pins["step"], GPIO.LOW)
        time.sleep(PULSE_DELAY_SEC)

    update_axis_status(axis, f"Done: moved {step_count} steps")
    axis_busy[axis] = False


def start_move(axis: str, step_sign: int) -> None:
    if axis_busy[axis]:
        return

    try:
        requested_steps = int(axis_step_vars[axis].get().strip())
    except ValueError:
        update_axis_status(axis, "Invalid step count")
        return

    if requested_steps <= 0:
        update_axis_status(axis, "Step count must be > 0")
        return

    step_count = requested_steps if step_sign > 0 else -requested_steps
    worker = threading.Thread(target=move_steps, args=(axis, step_count), daemon=True)
    worker.start()


def on_close() -> None:
    GPIO.cleanup()
    root.destroy()


root = tk.Tk()
root.title("Raspberry Pi 5 A4988 XYZ Control")
root.geometry("460x430")

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

for axis in ("X", "Y", "Z"):
    axis_step_vars[axis] = tk.StringVar(value="200")
    axis_status_vars[axis] = tk.StringVar(value=f"{axis}: Ready")

    frame = ttk.LabelFrame(main, text=f"{axis} Axis", padding=10)
    frame.pack(fill="x", pady=6)

    ttk.Label(frame, text="Steps per move").pack(anchor="w")
    ttk.Entry(frame, textvariable=axis_step_vars[axis], width=14).pack(anchor="w", pady=(2, 10))

    button_row = ttk.Frame(frame)
    button_row.pack(pady=(0, 8))
    ttk.Button(
        button_row, text=f"{axis} -", width=14, command=lambda a=axis: start_move(a, -1)
    ).pack(side="left", padx=6)
    ttk.Button(
        button_row, text=f"{axis} +", width=14, command=lambda a=axis: start_move(a, 1)
    ).pack(side="left", padx=6)

    ttk.Label(frame, textvariable=axis_status_vars[axis]).pack(anchor="w", fill="x")

setup_gpio()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

