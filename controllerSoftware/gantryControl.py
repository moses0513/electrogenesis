import tkinter as tk
from PIL import Image, ImageTk  # for logo display
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
root.geometry("400x600") # Window size
root.config(bg="#5E5E5E") # Background color

title = tk.Label(root, text="Stage Controller", fg="white", bg="#5E5E5E", font=("Arial", 16, "bold"))
title.pack(pady=10) 

# LOGO SECTION
try:
    logo_img = Image.open("egen25_logo.png")  # <-- your logo file name
    logo_img = logo_img.resize((360, 171))  # resize if needed
    logo_photo = ImageTk.PhotoImage(logo_img)

    logo_label = tk.Label(root, image=logo_photo, bg="#5E5E5E")
    logo_label.pack(pady=10)
except Exception as e:
    print(f"Could not load logo ⚠️ : {e}")

# MOVE COMMAND
frame = tk.Frame(root, bg="#5E5E5E") # Frame for movement buttons
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
z_frame = tk.LabelFrame(root, text="Z Axis", fg="white", bg="#5E5E5E", labelanchor="n", padx=10, pady=10)
z_frame.pack(pady=10)

tk.Button(z_frame, text="Z+", width=10, height=2,
          command=lambda: send_command("Z+50")).grid(row=0, column=0, padx=10, pady=5)
tk.Button(z_frame, text="Z-", width=10, height=2,
          command=lambda: send_command("Z-50")).grid(row=0, column=1, padx=10, pady=5)

root.mainloop() # Start the GUI event loop
