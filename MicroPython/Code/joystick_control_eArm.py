"""
eArm Robotic Arm Web Control System
Real-time button control with automatic servo adjustment
"""

from machine import Pin, PWM, ADC
import time
import _thread

# =============Joystick Hardware Pin Configuration ===============

# Left Joystick Configuration:
# Horizontal (Left-Right) axis connected to GPIO1 as analog input
left_lr = ADC(Pin(1))  # GPIO1: Left/Right movement of left joystick
# Vertical (Up-Down) axis connected to GPIO0 as analog input
left_ud = ADC(Pin(0))  # GPIO0: Up/Down movement of left joystick
# Button/Key press connected to GPIO8 as digital input
left_key = Pin(10, Pin.IN, Pin.PULL_UP)  # GPIO8: Button on left joystick

# Right Joystick Configuration:
# Horizontal (Left-Right) axis connected to GPIO3 as analog input
right_lr = ADC(Pin(3))  # GPIO3: Left/Right movement of right joystick
# Vertical (Up-Down) axis connected to GPIO2 as analog input
right_ud = ADC(Pin(2))  # GPIO2: Up/Down movement of right joystick
# Button/Key press connected to GPIO10 as digital input with internal pull-up resistor
right_key = Pin(8, Pin.IN, Pin.PULL_UP)  # GPIO10: Button on right joystick

# ==================== ADC Configuration ====================
# Configure ADC attenuation for 0-3.3V full range input
# ATTN_11DB allows measuring voltages from 0V to approximately 3.6V

# Left joystick ADC configuration
left_lr.atten(ADC.ATTN_11DB)  # Set full voltage range for left horizontal axis
left_ud.atten(ADC.ATTN_11DB)  # Set full voltage range for left vertical axis

# Right joystick ADC configuration
right_lr.atten(ADC.ATTN_11DB)  # Set full voltage range for right horizontal axis
right_ud.atten(ADC.ATTN_11DB)  # Set full voltage range for right vertical axis

# Note: ESP32-C3 ADC is 12-bit, returning values from 0 to 4095
# 0 = 0V, 4095 = 3.3V (approximately)


# ==================== Buzzer Control Class ====================
class Buzzer:
    """
    Simple buzzer controller using PWM for passive buzzers
    
    Passive buzzers require PWM signals to generate sound at different frequencies.
    This class provides basic beep functionality for user feedback.
    """
    
    def __init__(self, pin=8):
        """
        Initialize buzzer on specified GPIO pin
        
        Args:
            pin (int): GPIO pin number connected to buzzer positive terminal.
                      Buzzer negative terminal should be connected to GND.
                      Default is GPIO8.
        """
        # Create PWM object on specified pin
        self.pwm = PWM(Pin(pin))
        
        # Start with buzzer off (silent)
        self.off()
        
        print(f"Buzzer initialized on GPIO{pin}")
    
    def on(self, freq=1000):
        """
        Turn on buzzer with specified frequency
        
        Args:
            freq (int): Frequency in Hertz (Hz). Higher values produce higher pitch.
                       Default is 1000 Hz (typical beep frequency).
        
        Note:
            Passive buzzers require continuous PWM signal to produce sound.
            Duty cycle of 512 (50%) provides good volume without overloading.
        """
        # Set PWM frequency (determines pitch)
        self.pwm.freq(freq)
        
        # Set PWM duty cycle (512 = 50% = moderate volume)
        self.pwm.duty(512)
    
    def off(self):
        """
        Turn off buzzer (stop sound)
        
        Sets duty cycle to 0, which stops PWM signal and silences buzzer.
        """
        self.pwm.duty(0)
    
    def beep(self, freq=1000, duration=200):
        """
        Play a single beep
        
        Args:
            freq (int): Frequency in Hertz (Hz). Determines pitch of beep.
                       Default is 1000 Hz.
            duration (int): Duration in milliseconds (ms). How long the beep lasts.
                           Default is 200 ms.
        
        Usage:
            buzzer.beep()                    # Default beep (1000Hz, 200ms)
            buzzer.beep(800, 300)            # Lower pitch, longer beep
            buzzer.beep(1500, 100)           # Higher pitch, shorter beep
        """
        # Turn on buzzer with specified frequency
        self.on(freq)
        
        # Keep buzzer on for specified duration
        time.sleep_ms(duration)
        
        # Turn off buzzer
        self.off()
        

# ==================== Servo Control Class ====================
class Servo:
    """
    Servo motor control class with automatic adjustment capability
    Each servo runs its own control thread for smooth operation
    """
    
    def __init__(self, pin_num, freq=50, min_angle=0, max_angle=180, save_mode=0):
        """
        Initialize servo motor
        
        Args:
            pin_num (int): GPIO pin number for PWM signal
            freq (int): PWM frequency in Hz (default 50Hz for servos)
            min_angle (int): Minimum allowable angle (0-180)
            max_angle (int): Maximum allowable angle (0-180)
        """
        # Validate angle parameters
        if min_angle < 0 or max_angle > 180:
            raise ValueError("Angle range 0-180")
        if min_angle >= max_angle:
            raise ValueError("Min angle must be less than max angle")
            
        # Initialize GPIO pin as PWM output
        self.pin = Pin(pin_num, Pin.OUT)
        self.pwm = PWM(self.pin, freq=freq)
        
        # Store servo configuration
        self.freq = freq
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.current_angle = 90  # Default start position
        
        # Auto-control parameters
        self.auto_increase = False    # Flag for automatic angle increase
        self.auto_decrease = False    # Flag for automatic angle decrease
        self.running = True           # Thread running flag
        self.adjust_speed = 2         # Degrees to adjust per cycle (adjust for speed)
        
        # Calculate PWM timing parameters
        self.period_us = 1000000 // freq  # Period in microseconds
        self.min_pulse_us = 500      # Pulse width for 0 degrees (500μs)
        self.max_pulse_us = 2400     # Pulse width for 180 degrees (2400μs)
        
        # Safe mode to prevent the servo from getting clogged and hot
        self.save_mode = save_mode
        self.ticker = 0
        
        # Start the auto-adjustment thread
        _thread.start_new_thread(self._auto_adjust_thread, ())
        
    def _angle_to_duty(self, angle):
        """
        Convert angle to PWM duty cycle value
        
        Args:
            angle (float): Desired angle in degrees
        
        Returns:
            int: PWM duty cycle value (0-1023 for MicroPython)
        """
        # Clamp angle to allowable range
        if angle < self.min_angle:
            angle = self.min_angle
        elif angle > self.max_angle:
            angle = self.max_angle
            
        # Linear interpolation: angle -> pulse width
        pulse_width = self.min_pulse_us + (angle / 180) * (self.max_pulse_us - self.min_pulse_us)
        
        # Convert pulse width to duty cycle
        duty = int((pulse_width / self.period_us) * 1023)
        
        # Ensure duty stays within valid range
        if duty < 0:
            duty = 0
        elif duty > 1023:
            duty = 1023
            
        return duty
    
    def set_angle(self, angle, delay_ms=0,):
        """
        Set servo to specific angle
        
        Args:
            angle (float): Target angle in degrees
            delay_ms (int): Optional delay after setting angle
        
        Returns:
            float: Actual angle set (may differ if clamped)
        """
        duty = self._angle_to_duty(angle)
        self.pwm.duty(duty)
        self.current_angle = angle
        
        # Optional delay for smooth movement
        if delay_ms > 0:
            time.sleep_ms(delay_ms)
        return angle
    
    def _auto_adjust_thread(self):
        """
        Background thread for automatic angle adjustment
        Continuously adjusts angle when auto_increase or auto_decrease is True
        """
        while self.running:
            if self.auto_increase:
                # Automatic angle increase
                new_angle = self.current_angle + self.adjust_speed
                if new_angle > self.max_angle:
                    new_angle = self.max_angle
                self.set_angle(new_angle)
                time.sleep_ms(20)  # Control adjustment speed (lower = faster)
                self.ticker = 0
                
            elif self.auto_decrease:
                # Automatic angle decrease
                new_angle = self.current_angle - self.adjust_speed
                if new_angle < self.min_angle:
                    new_angle = self.min_angle
                self.set_angle(new_angle)
                time.sleep_ms(20)  # Control adjustment speed (lower = faster)
                self.ticker = 0
                
            else:
                # save_mode
                if self.save_mode == 1:
                    # After 40 seconds, turn off the pulse output
                    if self.ticker < 1000:
                        self.set_angle(self.current_angle)
                        time.sleep_ms(30)
                        self.ticker = self.ticker + 1
                    self.detach()
                    time.sleep_ms(10)
                # No active adjustment - sleep to save CPU
                else:                     
                    time.sleep_ms(50)
    
    def start_increase(self):
        """Start automatic angle increase"""
        self.auto_decrease = False
        self.auto_increase = True
    
    def start_decrease(self):
        """Start automatic angle decrease"""
        self.auto_increase = False
        self.auto_decrease = True
    
    def stop_adjust(self):
        """Stop all automatic adjustment"""
        self.auto_increase = False
        self.auto_decrease = False
    
    def adjust_angle(self, delta):
        """
        Manual angle adjustment (legacy method)
        
        Args:
            delta (float): Angle change (+ for increase, - for decrease)
        
        Returns:
            float: New angle after adjustment
        """
        new_angle = self.current_angle + delta
        if new_angle < self.min_angle:
            new_angle = self.min_angle
        elif new_angle > self.max_angle:
            new_angle = self.max_angle
        
        return self.set_angle(new_angle)
    
    def get_angle(self):
        """
        Get current servo angle
        
        Returns:
            float: Current angle in degrees
        """
        return self.current_angle
    
    def detach(self):
        """Stop PWM signal (servo can move freely)"""
        self.pwm.duty(0)
    
    def attach(self):
        """Reattach servo to current angle"""
        if self.current_angle is not None:
            self.set_angle(self.current_angle)
        else:
            self.set_angle(90)
    
    def deinit(self):
        """Clean up resources and stop control thread"""
        self.running = False
        time.sleep_ms(100)  # Allow thread to terminate
        self.detach()
        self.pwm.deinit()


# ==================== Servos Initialization ====================
# Initialize four servos on GPIO pins 4-7
servo_A = Servo(pin_num=4)  # Base rotation servo
servo_B = Servo(pin_num=5)  # Shoulder servo
servo_C = Servo(pin_num=6)  # Elbow servo
servo_D = Servo(pin_num=7, save_mode=1)  # Gripper/wrist servo

# ==================== Buzzer Initialization ====================
# Create buzzer instance on GPIO9
# Note: GPIO9 is used instead of GPIO8 as per user's code modification
buzzer = Buzzer(9)
buzzer_state = False

# The sensitivity of the joystick
sensitivity = 1800;  # 0-2048, the smaller the value, the more sensitive it is. 

# ==================== Main Program Loop ====================
def main():
    """
    Main program loop - runs web server and handles client connections
    """
    global sensitivity
    
    # Initialize all servos to center position (90 degrees)
    print("Initializing servos")
    servo_A.set_angle(90)
    servo_B.set_angle(120)
    servo_C.set_angle(60)
    servo_D.set_angle(90)
    
    # Main server loop
    while True:
        try:
            # servo_A control
            if left_lr.read() > 2048 + sensitivity:
                servo_A.start_increase()  # Start automatic increase
            elif left_lr.read() < 2048 - sensitivity:
                servo_A.start_decrease()  # Start automatic decrease
            else:
                servo_A.stop_adjust()     # Stop adjustment
                
            # servo_B control
            if left_ud.read() > 2048 + sensitivity:
                servo_B.start_increase()  # Start automatic increase
            elif left_ud.read() < 2048 - sensitivity:
                servo_B.start_decrease()  # Start automatic decrease
            else:
                servo_B.stop_adjust()     # Stop adjustment
                
            # servo_C control
            if right_ud.read() > 2048 + sensitivity:
                servo_C.start_decrease()  # Start automatic decrease
            elif right_ud.read() < 2048 - sensitivity:
                servo_C.start_increase()  # Start automatic increase
            else:
                servo_C.stop_adjust()     # Stop adjustment
                
            # servo_D control
            if right_lr.read() > 2048 + sensitivity:
                servo_D.start_increase()  # Start automatic increase
            elif right_lr.read() < 2048 - sensitivity:
                servo_D.start_decrease()  # Start automatic decrease
            else:
                servo_D.stop_adjust()     # Stop adjustment
            
            # buzzer
            if left_key.value() == 0:   # Eliminate key jitter
                buzzer.on()
            else:
                buzzer.off()

        except Exception as e:
            print("Server error:", e)


# ==================== Program Entry Point ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down eArm control system...")
        # Clean up all hardware resources
        servo_A.deinit()
        servo_B.deinit()
        servo_C.deinit()
        servo_D.deinit()
        buzzer_pin.value(0)  # Ensure buzzer is off
        print("All servos detached and buzzer turned off")
        print("System shutdown complete")
        