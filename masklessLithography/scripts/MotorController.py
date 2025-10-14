from machine import Pin, PWM
import utime


class MotorController:
    
    
    def __init__(self, stepGPIO=0, directionGPIO=1, ms1GPIO=None, ms2GPIO=None, ms3GPIO=None):
        
        self.directionPin = Pin(directionGPIO, Pin.OUT)
        self.stepPin = Pin(stepGPIO, Pin.OUT)
        self.ms1Pin = Pin(ms1GPIO, Pin.OUT) if ms1GPIO is not None else None
        self.ms2Pin = Pin(ms2GPIO, Pin.OUT) if ms2GPIO is not None else None
        self.ms3Pin = Pin(ms3GPIO, Pin.OUT) if ms3GPIO is not None else None
        
        
    def rotateMotor(self, steps=200, forwards=True, pulseMicroSeconds=400):
        
        self.directionPin.value(1 if forwards else 0)
        
        for _ in range(steps):
            
            self.stepPin.value(1)
            utime.sleep_us(pulseMicroSeconds)
            
            self.stepPin.value(0)
            utime.sleep_us(pulseMicroSeconds)
          
            
    def setMicrostepping(self, mode):
        
        modes = {
            
            'full': (0, 0, 0),
            'half': (1, 0, 0),
            'quarter': (0, 1, 0),
            'eighth': (1, 1, 0),
            'sixteenth': (1, 1, 1)
            
        }
        
        if mode not in modes:
            
            raise ValueError('Invalid microstepping mode')
        
        for pin, value in zip((self.ms1Pin, self.ms2Pin, self.ms3Pin), modes[mode]):
            
            if pin is not None:
                
                pin.value(value)
                
                
if __name__ == '__main__':
    
    motor1 = MotorController(stepGPIO=0, directionGPIO=1)
    motor2 = MotorController(stepGPIO=2, directionGPIO=3)
    motor3 = MotorController(stepGPIO=4, directionGPIO=5)
    
    motor1.rotateMotor(steps=200, forwards=False)
    #motor2.rotateMotor(steps=200, forwards=False)
    #motor3.rotateMotor(steps=200, forwards=False)