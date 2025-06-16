from machine import PWM, Pin

class Pump:
    
    def __init__(self, a2, a1, cyclespeed):
        self.a2 = Pin(a2, Pin.OUT)
        self.a1 = PWM(Pin(a1), freq = cyclespeed, duty = 256)

    
    def switchDirection(self):
        self.a2.value(1-self.a2.value())
    
    def setDirection(self, direction):
        self.a2.value(direction)
    
    def setSpeed(self, cyclespeed):
        self.a1.freq(cyclespeed)