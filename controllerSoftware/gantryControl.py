import tkinter as tk
import serial
import time

# SERIAL SETUP
# Change to your serial port (e.g., "COM3" on Windows or "/dev/ttyUSB0" on Pi)
try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1) # adjust as needed
    time.sleep(2)  # wait for connection
except:
    ser = None
    print(" No serial connection found ⚠️  . Running in GUI-only mode.")

# COMMAND FUNCTION
def send_command(command): # send command to microcontroller
    print(f"Sending: {command}")
    if ser:
        ser.write((command + '\n').encode())

# GUI SETUP
root = tk.Tk() # Main application window
root.title("Maskless Lithography Stage Controller") # Window title
root.geometry("400x350") # Window size
root.config(bg="#222") # Background color

title = tk.Label(root, text="Stage Controller", fg="white", bg="#222", font=("Arial", 16, "bold"))
title.pack(pady=10) 

# MOVE COMMAND
frame = tk.Frame(root, bg="#222") # Frame for movement buttons
frame.pack(pady=20) # Padding around frame

# Row 1: Y+
tk.Button(frame, text="↑ Y+", width=10, height=2,
          command=lambda: send_command("Y+100")).grid(row=0, column=1, padx=5, pady=5)

# Row 2: X-, stop, X+
tk.Button(frame, text="← X-", width=10, height=2,
          command=lambda: send_command("X-100")).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame, text="STOP", width=10, height=2, bg="red",
          command=lambda: send_command("STOP")).grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="→ X+", width=10, height=2,
          command=lambda: send_command("X+100")).grid(row=1, column=2, padx=5, pady=5)

# Row 3: Y-
tk.Button(frame, text="↓ Y-", width=10, height=2,
          command=lambda: send_command("Y-100")).grid(row=2, column=1, padx=5, pady=5)

# Z CONTROL
z_frame = tk.LabelFrame(root, text="Z Axis", fg="white", bg="#222", labelanchor="n", padx=10, pady=10)
z_frame.pack(pady=10)

tk.Button(z_frame, text="Z+", width=10, height=2,
          command=lambda: send_command("Z+50")).grid(row=0, column=0, padx=10, pady=5)
tk.Button(z_frame, text="Z-", width=10, height=2,
          command=lambda: send_command("Z-50")).grid(row=0, column=1, padx=10, pady=5)

root.mainloop() # Start the GUI event loop
