from machine import Pin
import time


class PumpStep:

    def __init__(self, direction_pin, step_pin):
        self.direction = Pin(direction_pin, Pin.OUT)
        self.step = Pin(step_pin, Pin.OUT)
    
    def onestep(self):
        self.step.value(1-self.step.value())


    def direction_right(self):
        self.direction.value(1)
    
    def direction_left(self):
        self.direction.value(0)
    
    def fullstep(self, numberOfSteps):

        for i in range(numberOfSteps):
            self.onestep()
            time.sleep(10)
            self.onestep()
            time.sleep(10)