"""
Simple Passive Buzzer Driver for ESP32-C3
Minimal implementation for basic audio feedback
"""

from machine import Pin, PWM
import time

class Buzzer:
    """
    Simple buzzer controller using PWM for passive buzzers
    
    Passive buzzers require PWM signals to generate sound at different frequencies.
    This class provides basic beep functionality for user feedback.
    """
    
    def __init__(self, pin=9):
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


# Avoid interfering with the servo
left_key = Pin(4, Pin.OUT)
left_key = Pin(5, Pin.OUT)
left_key = Pin(6, Pin.OUT)
left_key = Pin(7, Pin.OUT)

# ==================== Buzzer Initialization ====================
# Create buzzer instance on GPIO9
# Note: GPIO9 is used instead of GPIO8 as per user's code modification
buzzer = Buzzer(9)

# ==================== Test Loop ====================
# Continuous test sequence to verify buzzer functionality
while True:
    # Test 1: Default beep (1000Hz, 200ms)
    # Standard attention-getting beep
    buzzer.beep()
    
    # Wait 500ms between beeps for clear separation
    time.sleep_ms(500)
    
    # Test 2: Low pitch beep (800Hz, 300ms)
    # Lower frequency sounds "deeper" or "heavier"
    # Longer duration for more noticeable feedback
    buzzer.beep(800, 300)
    
    # Wait 500ms between beeps
    time.sleep_ms(500)
    
    # Test 3: High pitch beep (1500Hz, 100ms)
    # Higher frequency sounds "sharper" or "brighter"
    # Short duration for quick notifications
    buzzer.beep(1500, 100)
    
    # Wait 500ms before repeating test sequence
    time.sleep_ms(500)
