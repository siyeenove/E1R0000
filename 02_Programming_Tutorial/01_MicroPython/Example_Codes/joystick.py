"""
Simple eArm Joystick Reader for ESP32-C3
Reads analog and digital inputs from two joysticks
"""

from machine import Pin, ADC
import time

# ==================== Hardware Pin Configuration ====================
# Configure pins according to eArm hardware layout

# Left Joystick Configuration:
# Horizontal (Left-Right) axis connected to GPIO1 as analog input
left_lr = ADC(Pin(1))  # GPIO1: Left/Right movement of left joystick
# Vertical (Up-Down) axis connected to GPIO0 as analog input
left_ud = ADC(Pin(0))  # GPIO0: Up/Down movement of left joystick
# Button/Key press connected to GPIO8 as digital input
left_key = Pin(8, Pin.IN, Pin.PULL_UP)  # GPIO8: Button on left joystick

# Right Joystick Configuration:
# Horizontal (Left-Right) axis connected to GPIO3 as analog input
right_lr = ADC(Pin(3))  # GPIO3: Left/Right movement of right joystick
# Vertical (Up-Down) axis connected to GPIO2 as analog input
right_ud = ADC(Pin(2))  # GPIO2: Up/Down movement of right joystick
# Button/Key press connected to GPIO10 as digital input with internal pull-up resistor
right_key = Pin(10, Pin.IN, Pin.PULL_UP)  # GPIO10: Button on right joystick

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

# ==================== Main Program Loop ====================
# Continuously read and display joystick values
while True:
    # Read and display left joystick values
    
    # Read left joystick horizontal position (Left-Right axis)
    # Returns: 0 (fully left) to 4095 (fully right), ~2048 at center
    print("Left_joystick_LeftRight:", left_lr.read())
    
    # Read left joystick vertical position (Up-Down axis)
    # Returns: 0 (fully down) to 4095 (fully up), ~2048 at center
    print("Left_joystick_UpDown:", left_ud.read())
    
    # Read left joystick button state
    # Returns: 0 = button pressed, 1 = button released
    # Note: This depends on the physical wiring of the button
    print("Left_joystick_key:", left_key.value())
    
    # Read and display right joystick values
    
    # Read right joystick horizontal position (Left-Right axis)
    # Returns: 0 (fully left) to 4095 (fully right), ~2048 at center
    print("Right_joystick_LeftRight:", right_lr.read())
    
    # Read right joystick vertical position (Up-Down axis)
    # Returns: 0 (fully down) to 4095 (fully up), ~2048 at center
    print("Right_joystick_UpDown:", right_ud.read())
    
    # Read right joystick button state
    # Returns: 0 = button pressed, 1 = button released
    # Note: Using internal pull-up, so button press pulls pin LOW
    print("Right_joystick_key:", right_key.value())
    
    # Separator line for readability in serial output
    print("-" * 30)  # 30 dash characters
    
    # Wait for 1 second before next reading
    # This controls the sampling rate of the joysticks
    # Adjust this value for faster or slower updates
    time.sleep(1)