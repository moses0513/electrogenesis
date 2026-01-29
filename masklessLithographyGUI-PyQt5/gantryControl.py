import tkinter as tk
from PIL import Image, ImageTk  # for logo display
from mcu_side import move_motor
import os

X, Y, Z = 0, 0, 0 # XYZ coords of the gantry stage

# COMMAND FUNCTION
def moveMOTOR(command):
    print(f"Command: {command}")

    if command == "STOP":
        # Placeholder for future stop / estop logic
        return

    axis = command[0]        # 'X', 'Y', 'Z'
    direction = command[1]   # '+' or '-'
    steps = int(command[2:])

    move_motor(axis, direction, steps)

def datum():
    # Make all coordinates zero
    # Do this by subtracting their current position.
    move_motor('X', '-', X)
    move_motor('Y', '-', Y)
    move_motor('Z', '-', Z)

"""



# GUI SETUP
root = tk.Tk() # Main application window
root.title("Maskless Lithography Stage Controller") # Window title
root.geometry("400x600") # Window size
root.config(bg="#5E5E5E") # Background color

title = tk.Label(root, text="Stage Controller", fg="white", bg="#5E5E5E", font=("Arial", 16, "bold"))
title.pack(pady=10) 

# LOGO SECTION
try:
    # script_dir: directory where this .py lives (fallback to cwd if __file__ missing)
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    image_path = os.path.join(script_dir, "egen25_logo.png")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"{image_path} not found")

    logo_img = Image.open(image_path)
    logo_img = logo_img.resize((360, 171))
    logo_photo = ImageTk.PhotoImage(logo_img)

    logo_label = tk.Label(root, image=logo_photo, bg="#5E5E5E")
    logo_label.image = logo_photo  # keep a reference
    logo_label.pack(pady=10)
except Exception as e:
    print(f"Could not load logo ⚠️ : {e}")

# MOVE COMMAND
frame = tk.Frame(root, bg="#5E5E5E") # Frame for movement buttons
frame.pack(pady=20) # Padding around frame

# Row 1: Y+
tk.Button(frame, text="↑ Y+", width=10, height=2,
          command=lambda: moveMOTOR("Y+100")).grid(row=0, column=1, padx=5, pady=5)

# Row 2: X-, stop, X+
tk.Button(frame, text="← X-", width=10, height=2,
          command=lambda: moveMOTOR("X-100")).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame, text="STOP", width=10, height=2, bg="red",
          command=lambda: moveMOTOR("STOP")).grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="→ X+", width=10, height=2,
          command=lambda: moveMOTOR("X+100")).grid(row=1, column=2, padx=5, pady=5)
# Row 3: Y-
tk.Button(frame, text="↓ Y-", width=10, height=2,
          command=lambda: moveMOTOR("Y-100")).grid(row=2, column=1, padx=5, pady=5)

# Z CONTROL
z_frame = tk.LabelFrame(root, text="Z Axis", fg="white", bg="#5E5E5E", labelanchor="n", padx=10, pady=10)
z_frame.pack(pady=10)

tk.Button(z_frame, text="Z+", width=10, height=2,
          command=lambda: moveMOTOR("Z+50")).grid(row=0, column=0, padx=10, pady=5)
tk.Button(z_frame, text="Z-", width=10, height=2,
          command=lambda: moveMOTOR("Z-50")).grid(row=0, column=1, padx=10, pady=5)

# KEYBOARD SHORTCUTS
root.bind("<Up>", lambda e: moveMOTOR("Y+100"))
root.bind("<Down>", lambda e: moveMOTOR("Y-100"))
root.bind("<Left>", lambda e: moveMOTOR("X-100"))
root.bind("<Right>", lambda e: moveMOTOR("X+100"))
root.bind("<Prior>", lambda e: moveMOTOR("Z+50"))   # Page Up
root.bind("<Next>", lambda e: moveMOTOR("Z-50"))    # Page Down

root.mainloop() # Start the GUI event loop

# To package with PyInstaller including the logo image, use:
# python -m PyInstaller --add-data "egen25_logo.png;." gantryControl.py



"""