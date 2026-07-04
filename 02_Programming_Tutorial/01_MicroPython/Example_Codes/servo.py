from machine import Pin, PWM
import time

class Servo:
    """
    Servo control class
    For ESP32-C3 MicroPython servo control
    """
    
    def __init__(self, pin_num, freq=50, min_angle=0, max_angle=180):
        """
        Initialize servo
        
        Parameters:
            pin_num: GPIO pin number (e.g., 1, 2, 3...)
            freq: PWM frequency, default 50Hz (standard servo frequency)
            min_angle: Minimum angle, default 0 degrees
            max_angle: Maximum angle, default 180 degrees
        """
        # Validate parameters
        if min_angle < 0 or max_angle > 180:
            raise ValueError("Angle range should be 0-180 degrees")
        if min_angle >= max_angle:
            raise ValueError("Minimum angle must be less than maximum angle")
            
        # Initialize pin and PWM
        self.pin = Pin(pin_num, Pin.OUT)
        self.pwm = PWM(self.pin, freq=freq)
        
        # Servo parameters
        self.freq = freq
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.current_angle = None  # Current angle
        
        # Calculate period time (microseconds)
        self.period_us = 1000000 // freq  # e.g., 50Hz = 20000us
        
        # Default servo parameters (0.5ms-2.4ms pulse width)
        self.min_pulse_us = 500    # Pulse width at 0 degrees
        self.max_pulse_us = 2400   # Pulse width at 180 degrees
        
    def _angle_to_duty(self, angle):
        """
        Convert angle to PWM duty value
        
        Parameters:
            angle: Target angle (0-180 degrees)
        Returns:
            duty: PWM duty value
        """
        # Limit angle within allowed range
        if angle < self.min_angle:
            angle = self.min_angle
        elif angle > self.max_angle:
            angle = self.max_angle
            
        # Calculate pulse width (microseconds)
        # Linear mapping: angle -> pulse width
        pulse_width = self.min_pulse_us + (angle / 180) * (self.max_pulse_us - self.min_pulse_us)
        
        # Calculate duty cycle (duty = pulse width / period)
        # MicroPython's duty() method requires value 0-1023
        duty = int((pulse_width / self.period_us) * 1023)
        
        # Ensure duty is within valid range
        if duty < 0:
            duty = 0
        elif duty > 1023:
            duty = 1023
            
        return duty
    
    def set_angle(self, angle, delay_ms=0):
        """
        Set servo angle
        
        Parameters:
            angle: Target angle (0-180 degrees)
            delay_ms: Delay time after setting (milliseconds)
        Returns:
            Actual set angle
        """
        # Calculate and set duty cycle
        duty = self._angle_to_duty(angle)
        self.pwm.duty(duty)
        
        # Update current angle
        self.current_angle = angle
        
        # If delay is needed
        if delay_ms > 0:
            time.sleep_ms(delay_ms)
            
        return angle
    
    def get_angle(self):
        """
        Get current angle
        Returns: Current angle, returns None if not set
        """
        return self.current_angle
    
    def detach(self):
        """Detach servo (stop PWM output)"""
        self.pwm.duty(0)
    
    def attach(self):
        """Reattach servo (restore PWM output)"""
        if self.current_angle is not None:
            self.set_angle(self.current_angle)
        else:
            self.set_angle(90)
    
    def deinit(self):
        """Release resources"""
        self.detach()
        self.pwm.deinit()


# Create servo objects connected to GPIO pins
# Each servo object controls one motor, with each assigned to a specific GPIO pin
# Initialize servo A connected to GPIO pin 4 (e.g., base rotation)
servo_A = Servo(pin_num=4)
# Initialize servo B connected to GPIO pin 5 (e.g., shoulder joint)
servo_B = Servo(pin_num=5)
# Initialize servo C connected to GPIO pin 6 (e.g., elbow joint)
servo_C = Servo(pin_num=6)
# Initialize servo D connected to GPIO pin 7 (e.g., gripper/claw)
servo_D = Servo(pin_num=7)

# Set initial positions for all servos to avoid sudden movements on startup
# Set servo A to 90 degrees (midpoint/neutral position)
servo_A.set_angle(90)
# Set servo B to 120 degrees (typical raised/ready position for shoulder)
servo_B.set_angle(120)
# Set servo C to 120 degrees (typical bent position for elbow)
servo_C.set_angle(120)
# Set servo D to 90 degrees (midpoint position for gripper, likely partially open)
servo_D.set_angle(90)
        
# Test loop (same as original code)
while True:
    # Slowly rotate servo C through its full range (0-180 degrees)
    # First, move from 0 to 180 degrees (forward sweep)
    for angle in range(0, 181, 1):
        # Set servo C to the current angle position
        servo_C.set_angle(angle)
        # Pause for 25 milliseconds to create smooth, slow motion
        time.sleep(0.025)

    # Then, move back from 180 to 0 degrees (reverse sweep)  
    for angle in range(180, 0, -1):
        # Set servo C to the current angle position (decreasing)
        servo_C.set_angle(angle)
        # Pause for 25 milliseconds to maintain consistent speed
        time.sleep(0.025)
