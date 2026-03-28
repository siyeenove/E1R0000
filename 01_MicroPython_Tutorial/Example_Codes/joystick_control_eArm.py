# joystick_control_eArm.py
# MicroPython version for ESP32-C3
# This code applies to siyeenove mechanical arm
# Through this link you can download the source code:
# https://github.com/siyeenove
# Company web site:
# https://siyeenove.com/
from machine import Pin, ADC, PWM
import time

class JoyStick:
    """Joystick class"""
    def __init__(self):
        self.pin_x = None
        self.pin_y = None
        self.pin_z = None
        self.adc_x = None
        self.adc_y = None
        self.btn_z = None
        self.buf = [0] * 20
    
    def attach(self, x_pin, y_pin, z_pin=None):
        """Attach joystick pins"""
        self.pin_x = x_pin
        self.pin_y = y_pin
        self.adc_x = ADC(Pin(x_pin))
        self.adc_y = ADC(Pin(y_pin))
        self.adc_x.atten(ADC.ATTN_11DB)  # 0-3.3V range
        self.adc_y.atten(ADC.ATTN_11DB)
        
        if z_pin is not None:
            self.pin_z = z_pin
            self.btn_z = Pin(z_pin, Pin.IN, Pin.PULL_UP)
    
    def _eliminate_jitter(self):
        """Eliminate jitter, take average of middle 10 values"""
        total = 0
        for i in range(5, 15):
            total += self.buf[i]
        return total // 10
    
    def read_x(self):
        """Read X-axis value"""
        for i in range(20):
            self.buf[i] = self.adc_x.read()
        return self._eliminate_jitter()
    
    def read_y(self):
        """Read Y-axis value"""
        for i in range(20):
            self.buf[i] = self.adc_y.read()
        return self._eliminate_jitter()
    
    def read_z(self):
        """Read Z-axis button (False when pressed, True when released)"""
        if self.btn_z:
            return self.btn_z.value()  # Pull-up resistor, 0 when pressed
        return 1


class Servo:
    """Servo class"""
    def __init__(self, pin, min_us=500, max_us=2400, freq=50):
        self.pin = pin
        self.pwm = PWM(Pin(pin), freq=freq)
        self.min_us = min_us
        self.max_us = max_us
        self.current_angle = 90
        self._write_us(self._angle_to_us(90))
    
    def _angle_to_us(self, angle):
        """Convert angle to microseconds"""
        angle = max(0, min(180, angle))
        return int(self.min_us + (angle / 180) * (self.max_us - self.min_us))
    
    def _write_us(self, us):
        """Write microseconds to PWM"""
        # ESP32-C3 PWM resolution is 16-bit, period 20ms = 20000us
        duty = int(us / 20000 * 65535)
        self.pwm.duty_u16(duty)
    
    def write(self, angle):
        """Set servo angle"""
        self.current_angle = max(0, min(180, angle))
        self._write_us(self._angle_to_us(self.current_angle))
    
    def read(self):
        """Read current angle"""
        return self.current_angle
    
    def release(self):
        """Release servo (stop PWM)"""
        self.pwm.duty_u16(0)


class eArm:
    """Mechanical arm control class"""
    def __init__(self):
        self.servo_current_angle = [90, 120, 60, 90]  # A, B, C, D servos
        self.A_servo = None
        self.B_servo = None
        self.C_servo = None
        self.D_servo = None
        self.JoyStickL = None
        self.JoyStickR = None
    
    def joy_stick_attach(self, xpin1, ypin1, zpin1, xpin2, ypin2, zpin2):
        """Attach joysticks with Z-axis buttons"""
        self.JoyStickL = JoyStick()
        self.JoyStickR = JoyStick()
        self.JoyStickL.attach(xpin1, ypin1, zpin1)
        self.JoyStickR.attach(xpin2, ypin2, zpin2)
    
    def servo_attach(self, A_pin, B_pin, C_pin, D_pin):
        """Attach servo motors"""
        # Initialize all servos
        self.A_servo = Servo(A_pin)
        self.B_servo = Servo(B_pin)
        self.C_servo = Servo(C_pin)
        self.D_servo = Servo(D_pin)
        
        # Set initial angles
        self.A_servo.write(self.servo_current_angle[0])
        self.B_servo.write(self.servo_current_angle[1])
        self.C_servo.write(self.servo_current_angle[2])
        self.D_servo.write(self.servo_current_angle[3])
    
    # Upper Arm
    def ua_up(self, speed):
        """Move arm up"""
        self.servo_current_angle[1] += 1
        if self.servo_current_angle[1] >= 180:
            self.servo_current_angle[1] = 180
        self.B_servo.write(self.servo_current_angle[1])
        time.sleep_ms(speed)
     
    # Forearm
    def fa_up(self, speed):
        """Move arm up"""
        self.servo_current_angle[2] -= 1
        if self.servo_current_angle[2] <= 0:
            self.servo_current_angle[2] = 0
        self.C_servo.write(self.servo_current_angle[2])
        time.sleep_ms(speed)
    
    # Upper Arm
    def ua_down(self, speed):
        """Move arm down"""
        self.servo_current_angle[1] -= 1
        if self.servo_current_angle[1] <= 0:
            self.servo_current_angle[1] = 0
        self.B_servo.write(self.servo_current_angle[1])
        time.sleep_ms(speed)
    
    # Forearm
    def fa_down(self, speed):
        """Move arm down"""
        self.servo_current_angle[2] += 1
        if self.servo_current_angle[2] >= 180:
            self.servo_current_angle[2] = 180
        self.C_servo.write(self.servo_current_angle[2])
        time.sleep_ms(speed)
    
    def left(self, speed):
        """Rotate arm left"""
        self.servo_current_angle[0] += 1
        if self.servo_current_angle[0] >= 180:
            self.servo_current_angle[0] = 180
        self.A_servo.write(self.servo_current_angle[0])
        time.sleep_ms(speed)
    
    def right(self, speed):
        """Rotate arm right"""
        self.servo_current_angle[0] -= 1
        if self.servo_current_angle[0] <= 0:
            self.servo_current_angle[0] = 0
        self.A_servo.write(self.servo_current_angle[0])
        time.sleep_ms(speed)
    
    def claw_open(self, speed):
        """Open claw"""
        self.servo_current_angle[3] += 1
        if self.servo_current_angle[3] >= 180:
            self.servo_current_angle[3] = 180
        self.D_servo.write(self.servo_current_angle[3])
        time.sleep_ms(speed)
    
    def claw_close(self, speed):
        """Close claw"""
        self.servo_current_angle[3] -= 1
        if self.servo_current_angle[3] <= 0:
            self.servo_current_angle[3] = 0
        self.D_servo.write(self.servo_current_angle[3])
        time.sleep_ms(speed)
    
    def claw_release(self):
        """Release claw servo to prevent overheating"""
        if self.D_servo:
            self.D_servo.release()
    
    def record_action(self):
        """Record current action, return angle list"""
        return self.servo_current_angle.copy()
    
    def execution_action(self, angles, speed):
        """Execute recorded action"""
        # Copy target angles to list
        target_angles = angles.copy()
        
        moving = True
        while moving:
            moving = False
            # Update each servo angle
            for i in range(4):
                if self.servo_current_angle[i] != target_angles[i]:
                    moving = True
                    # Move one step in the direction of the target
                    if target_angles[i] > self.servo_current_angle[i]:
                        self.servo_current_angle[i] += 1
                    else:
                        self.servo_current_angle[i] -= 1
            
            # Write to servos
            self.A_servo.write(self.servo_current_angle[0])
            self.B_servo.write(self.servo_current_angle[1])
            self.C_servo.write(self.servo_current_angle[2])
            self.D_servo.write(self.servo_current_angle[3])
            
            time.sleep_ms(speed)
        
        time.sleep_ms(speed * 20)


# Initialize mechanical arm
arm = eArm()

# Servo motor connection pins (adjust according to actual wiring)
arm.servo_attach(4, 5, 6, 7)

# Joystick connection pins: xL, yL, zL, xR, yR, zR (adjust according to actual wiring)
arm.joy_stick_attach(0, 1, 10, 2, 3, 8)

# Global variables
xL = 0
yL = 0
xR = 0
yR = 0

# Buzzer pin
buzzer_pin = Pin(9, Pin.OUT)
buzzer_pin.value(1)

# Action recording array
ACT_MAX = 20  # Default 20 actions, 4 angles per servo, MAX = 2500
act = [[0]*4 for _ in range(ACT_MAX)]  # 2D array for storing actions
num = 0  # Current action index
num_do = 0  # Number of recorded actions
t_claw = 0  # Timestamp for claw operation

# Upper Arm
def turn_ua_ud():
    """Up/Down control"""
    global xL
    if xL <= 1500 or xL > 2595:
        if 0 <= xL <= 300:
            arm.ua_down(10)
        elif 3795 < xL <= 4095:
            arm.ua_up(10)
        elif 300 < xL <= 600:
            arm.ua_up(20)
        elif 3495 < xL <= 3795:
            arm.ua_down(20)
        elif 600 < xL <= 900:
            arm.ua_up(25)
        elif 3195 < xL <= 3495:
            arm.ua_down(25)
        elif 900 < xL <= 1200:
            arm.ua_up(30)
        elif 2895 < xL <= 3195:
            arm.ua_down(30)
        elif 1200 < xL <= 1500:
            arm.ua_up(35)
        elif 2595 < xL <= 2895:
            arm.ua_down(35)

# Forearm
def turn_fa_ud():
    """Up/Down control"""
    global xR
    if xR <= 1500 or xR > 2595:
        if 0 <= xR <= 300:
            arm.fa_down(10)
        elif 3795 < xR <= 4095:
            arm.fa_up(10)
        elif 300 < xR <= 600:
            arm.fa_up(20)
        elif 3495 < xR <= 3795:
            arm.fa_down(20)
        elif 600 < xR <= 900:
            arm.fa_up(25)
        elif 3195 < xR <= 3495:
            arm.fa_down(25)
        elif 900 < xR <= 1200:
            arm.fa_up(30)
        elif 2895 < xR <= 3195:
            arm.fa_down(30)
        elif 1200 < xR <= 1500:
            arm.fa_up(35)
        elif 2595 < xR <= 2895:
            arm.fa_down(35)
            
def turn_lr():
    """Left/Right control"""
    global yL
    if yL <= 1500 or yL > 2595:
        if 0 <= yL <= 300:
            arm.right(5)
        elif 3795 < yL <= 4095:
            arm.left(5)
        elif 300 < yL <= 600:
            arm.right(10)
        elif 3495 < yL <= 3795:
            arm.left(10)
        elif 600 < yL <= 900:
            arm.right(15)
        elif 3195 < yL <= 3495:
            arm.left(15)
        elif 900 < yL <= 1200:
            arm.right(20)
        elif 2895 < yL <= 3195:
            arm.left(20)
        elif 1200 < yL <= 1500:
            arm.right(25)
        elif 2595 < yL <= 2895:
            arm.left(25)


def claw():
    """Claw control"""
    global t_claw, yR
    
    if yR <= 1500 or yR > 2595:
        if 0 <= yR <= 300:
            arm.claw_close(0)
        elif 3795 < yR <= 4095:
            arm.claw_open(0)
        elif 300 < yR <= 600:
            arm.claw_close(5)
        elif 3495 < yR <= 3795:
            arm.claw_open(5)
        elif 600 < yR <= 900:
            arm.claw_close(10)
        elif 3195 < yR <= 3495:
            arm.claw_open(10)
        elif 900 < yR <= 1200:
            arm.claw_close(15)
        elif 2895 < yR <= 3195:
            arm.claw_open(15)
        elif 1200 < yR <= 1500:
            arm.claw_close(20)
        elif 2595 < yR <= 2895:
            arm.claw_open(20)
        
        t_claw = time.ticks_ms()
    
    # Prevent claw servo from overheating
    if t_claw != 0 and time.ticks_diff(time.ticks_ms(), t_claw) > 40000:
        arm.claw_release()


def data_processing(x, y):
    """Data processing, prioritize axis with larger change"""
    if abs(2048 - x) > abs(2048 - y):
        return x, 2048
    else:
        return 2048, y


def buzzer(h, l):
    """Buzzer sound"""
    global yR
    
    while not arm.JoyStickL.read_z():
        buzzer_pin.value(0)
        time.sleep_us(h)
        buzzer_pin.value(1)
        time.sleep_us(l)
    
    while not arm.JoyStickR.read_z():
        buzzer_pin.value(0)
        time.sleep_us(h)
        buzzer_pin.value(1)
        time.sleep_us(l)


def record_action():
    """Record action"""
    global num, num_do
    
    if not arm.JoyStickL.read_z():
        buzzer(600, 400)
        
        # Record current action
        angles = arm.record_action()
        for i in range(4):
            act[num][i] = angles[i]
        
        num += 1
        num_do = num
        
        # Check if maximum actions reached
        if num >= ACT_MAX:
            num = ACT_MAX
            # Long beep to indicate full memory
            for i in range(2000):
                buzzer_pin.value(0)
                time.sleep_us(600)
                buzzer_pin.value(1)
                time.sleep_us(400)
        
        # Wait for button release
        while not arm.JoyStickL.read_z():
            time.sleep_ms(10)


def execute_action():
    """Execute recorded action with long press exit functionality"""
    if not arm.JoyStickR.read_z():
        buzzer(200, 300)
        
        # If no actions are recorded, return.
        if num_do == 0:
            print("No actions recorded!")
            # Wait for button release after initial press
            while not arm.JoyStickR.read_z():
                time.sleep_ms(10)
            
            time.sleep_ms(500)
            
            # exit beep and return
            for _ in range(2000):
                buzzer_pin.value(0)
                time.sleep_us(200)
                buzzer_pin.value(1)
                time.sleep_us(300)
            return
        
        # Wait for button release after initial press
        while not arm.JoyStickR.read_z():
            time.sleep_ms(10)
        
        # Main loop - repeats the recorded actions
        while True:
            for i in range(num_do):
                arm.execution_action(act[i], 15)
                
                button_t = time.ticks_ms()  # Record the start time
                # Check for long press during action execution
                while not arm.JoyStickR.read_z():
                    if time.ticks_diff(time.ticks_ms(), button_t) > 2000:
                        # Long press detected - exit beep and return
                        for _ in range(2000):
                            buzzer_pin.value(0)
                            time.sleep_us(200)
                            buzzer_pin.value(1)
                            time.sleep_us(300)
                        
                        # Wait for button release
                        while not arm.JoyStickR.read_z():
                            time.sleep_ms(10)
                        return


def setup():
    """Initialization"""
    # No need for serial initialization in MicroPython
    # Servo and joystick are already attached in global initialization
    pass


# Main loop
print("Mechanical Arm Control System Started")
print("Use joysticks to control the arm")
print("Left joystick button: Record action")
print("Right joystick button: Execute recorded actions")

# Call setup
setup()

# Main loop
while True:
    try:
        # Read joystick values
        xL = arm.JoyStickL.read_x()
        yL = arm.JoyStickL.read_y()
        xR = arm.JoyStickR.read_x()
        yR = arm.JoyStickR.read_y()
        
        # Data processing
        xL, yL = data_processing(xL, yL)
        xR, yR = data_processing(xR, yR)
        
        # Execute controls
        turn_lr()
        turn_ua_ud()
        turn_fa_ud()
        claw()
        
        # Action recording and execution
        record_action()
        execute_action()
        
        # Small delay to avoid CPU overload
        time.sleep_ms(5)
        
    except KeyboardInterrupt:
        print("\nProgram stopped")
        break
    except Exception as e:
        print("Error:", e)
        time.sleep_ms(100)

