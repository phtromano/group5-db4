from machine import Pin,PWM

class RGB_Led:
    def __init__(self):
        self.red = PWM(Pin(15))
        self.blue = PWM(Pin(32))
        self.green = PWM(Pin(14))
    
    def turn_off_led(self):
        self.red.duty(0)
        self.blue.duty(0)
        self.green.duty(0)
    
    def turn_on_led(self):
        self.red.duty(1023)
        self.blue.duty(0)
        self.green.duty(0)
