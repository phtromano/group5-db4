from machine import Pin
import time


class SubPump:

    def __init__(self, a2, a1):
        self.a2 = Pin(a2, Pin.OUT)
        self.a1 = Pin(a1, Pin.OUT)
    
    def onestep(self):
        self.a1.value(1-self.a1.value())


    def direction_right(self):
        self.a2.value(1)
    
    def direction_left(self):
        self.a2.value(0)
    
    def fullstep(self, numberOfSteps):

        for i in range(numberOfSteps):
            self.onestep()
            time.sleep(10)
            self.onestep()
            time.sleep(10)