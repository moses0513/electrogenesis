import smbus2
import time

AS5600_ADDR = 0x36
RAW_ANGLE_HIGH = 0x0E
RAW_ANGLE_LOW = 0x0F

# Create I2C bus (1 is typically the default I2C bus on Raspberry Pi)
# Use 0 if on some other boards
i2c = smbus2.SMBus(1)

def read_angle():
    """Read angle from AS5600 magnetic encoder"""
    try:
        high = i2c.read_byte_data(AS5600_ADDR, RAW_ANGLE_HIGH)
        low = i2c.read_byte_data(AS5600_ADDR, RAW_ANGLE_LOW)
        
        raw_angle = (high << 8) | low
        angle_deg = raw_angle * 360 / 4096
        
        return raw_angle, angle_deg
    except Exception as e:
        print(f"Error reading from AS5600: {e}")
        return None, None

try:
    while True:
        raw, deg = read_angle()
        if raw is not None:
            print(f"Raw angle: {raw} -> Degrees: {round(deg, 2)}")
        time.sleep(0.2)
        
except KeyboardInterrupt:
    print("\nProgram stopped by user")
    i2c.close()