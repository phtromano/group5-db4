from machine import Pin,PWM


#red = PWM(Pin(27))
##blue = PWM(Pin(33))
#green = PWM(Pin(32))
    
    
    
#red.duty(1023)
#blue.duty(0)
#green.duty(0)

import rgbLed

rgb = rgbLed()
rgb.turn_on_led()


