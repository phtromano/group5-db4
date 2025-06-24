from machine import Pin, PWM

class Servo:
    """
    Simple servo motor controller using PWM on ESP32 with MicroPython.

    Usage:
        srv = Servo(pin=14)
        srv.set_angle(90)  # Move to mid-point (90 degrees)
        srv.off()          # Stop sending PWM (freewheel)
    """
    def __init__(self, pin, freq=50, min_us=500, max_us=2500, angle_range=180):
        """
        Initialize the Servo instance.

        Args:
            pin (int): GPIO pin connected to servo signal line.
            freq (int): PWM frequency in Hz (standard 50Hz for servos).
            min_us (int): Pulse width in microseconds corresponding to 0 degrees.
            max_us (int): Pulse width in microseconds corresponding to max angle.
            angle_range (int): Maximum servo angle (default 180).
        """
        self.pwm = PWM(Pin(pin), freq=freq)
        self.min_us = min_us
        self.max_us = max_us
        self.angle_range = angle_range
        self.period = 1000000 // freq  # Period in microseconds

    def _duty_for_us(self, us):
        """
        Convert a pulse width in microseconds to a duty cycle (0-1023).
        """
        return int((us / self.period) * 1023)

    def set_angle(self, angle):
        """
        Set the servo to a specific angle.

        Args:
            angle (int or float): Desired angle between 0 and angle_range.
        """
        if angle < 0:
            angle = 0
        elif angle > self.angle_range:
            angle = self.angle_range
        # Map angle to pulse width
        us = self.min_us + (self.max_us - self.min_us) * (angle / self.angle_range)
        duty = self._duty_for_us(us)
        self.pwm.duty(duty)

    def off(self):
        """
        Stop PWM, allowing the servo to freewheel.
        """
        self.pwm.deinit()



## Example usage
# if __name__ == "__main__":
#     # Initialize servo on GPIO14
#     servo = Servo(pin=14)

#     # Sweep from 0 to 180 degrees
#     import time
#     for angle in range(0, 181, 10):
#         servo.set_angle(angle)
#         time.sleep(0.5)
#     # Return to 90
#     servo.set_angle(90)
#     time.sleep(1)

#     # Turn off PWM
#     servo.off()
