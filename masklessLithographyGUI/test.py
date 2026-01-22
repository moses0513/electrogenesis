import tkinter as tk
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
import time
import os

# --------------------------
# SERIAL HANDLING (connect, send, disconnect)
# --------------------------
def find_pico_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "COM6" in p.description or "RP2" in p.description or "Pico" in p.description:
            return p.device
    return None

def send_command(command):
    port = find_pico_port()
    if not port:
        print("⚠️ Pico not found.")
        return

    try:
        # Connect
        with serial.Serial(port, 115200, timeout=1) as ser:
            time.sleep(2)  # wait for Pico to reset
            print(f"🔗 Connected to Pico on {port}")
            
            # Send command
            ser.write((command + "\n").encode())
            print(f"➡️ Sent command: {command}")

            # Optional: wait briefly for Pico to acknowledge/move
            time.sleep(0.2)

            # Disconnect automatically when exiting 'with'
            print("🔌 Disconnected from Pico")
    except Exception as e:
        print(f"⚠️ Serial error: {e}")

# --------------------------
# GUI SETUP
# --------------------------
root = tk.Tk()
root.title("Maskless Lithography Stage Controller")
root.geometry("400x600")
root.config(bg="#5E5E5E")

# Title
title = tk.Label(root, text="Stage Controller", fg="white", bg="#5E5E5E", font=("Arial", 16, "bold"))
title.pack(pady=10)

# Logo
try:
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    image_path = os.path.join(script_dir, "egen25_logo.png")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"{image_path} not found")

    logo_img = Image.open(image_path)
    logo_img = logo_img.resize((360, 171))
    logo_photo = ImageTk.PhotoImage(logo_img)

    logo_label = tk.Label(root, image=logo_photo, bg="#5E5E5E")
    logo_label.image = logo_photo
    logo_label.pack(pady=10)
except Exception as e:
    print(f"Could not load logo ⚠️ : {e}")

# --------------------------
# MOVE COMMAND BUTTONS
# --------------------------
frame = tk.Frame(root, bg="#5E5E5E")
frame.pack(pady=20)

tk.Button(frame, text="↑ Y+", width=10, height=2, command=lambda: send_command("Y+100")).grid(row=0, column=1)
tk.Button(frame, text="← X-", width=10, height=2, command=lambda: send_command("X-100")).grid(row=1, column=0)
tk.Button(frame, text="STOP", width=10, height=2, bg="red", command=lambda: send_command("STOP")).grid(row=1, column=1)
tk.Button(frame, text="→ X+", width=10, height=2, command=lambda: send_command("X+100")).grid(row=1, column=2)
tk.Button(frame, text="↓ Y-", width=10, height=2, command=lambda: send_command("Y-100")).grid(row=2, column=1)

z_frame = tk.LabelFrame(root, text="Z Axis", fg="white", bg="#5E5E5E", labelanchor="n", padx=10, pady=10)
z_frame.pack(pady=10)
tk.Button(z_frame, text="Z+", width=10, height=2, command=lambda: send_command("Z+50")).grid(row=0, column=0)
tk.Button(z_frame, text="Z-", width=10, height=2, command=lambda: send_command("Z-50")).grid(row=0, column=1)

# --------------------------
# KEYBOARD SHORTCUTS
# --------------------------
root.bind("<Up>", lambda e: send_command("Y+100"))
root.bind("<Down>", lambda e: send_command("Y-100"))
root.bind("<Left>", lambda e: send_command("X-100"))
root.bind("<Right>", lambda e: send_command("X+100"))
root.bind("<Prior>", lambda e: send_command("Z+50"))   # Page Up
root.bind("<Next>", lambda e: send_command("Z-50"))    # Page Down

# --------------------------
# CLEAN EXIT
# --------------------------
def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# --------------------------
# RUN GUI
# --------------------------
root.mainloop()
