from machine import Pin, I2C
import time

AS5600_ADDR = 0x36
RAW_ANGLE_HIGH = 0x0E
RAW_ANGLE_LOW = 0x0F

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

def read_angle():
    high = i2c.readfrom_mem(AS5600_ADDR, RAW_ANGLE_HIGH, 1)[0]
    low  = i2c.readfrom_mem(AS5600_ADDR, RAW_ANGLE_LOW, 1)[0]
    raw_angle = (high << 8) | low
    angle_deg = raw_angle * 360 / 4096
    return raw_angle, angle_deg

while True:
    raw, deg = read_angle()
    print("Raw angle:", raw, " -> Degrees:", round(deg, 2))
    time.sleep(0.2)
