import machine
import as5600  # Assuming the library is named as5600

# Initialize I2C
# Replace with your actual SDA and SCL pins
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0)) 

# Create an instance of the sensor
# Using the default I2C address (0x36)
try:
    sensor = as5600.AS5600(i2c) 
except ValueError:
    print("AS5600 not found. Check wiring and I2C address.")

# Main loop to read the angle
while True:
    angle = sensor.readAngle()  # Reads the angle in degrees (0-360)
    print("Angle:", angle)
    time.sleep(0.1)
