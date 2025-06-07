import tkinter as tk
from pyfirmata2 import Arduino, OUTPUT, PWM, util
import time

# Set up the Arduino board with a try-except block
port = '/dev/ttyUSB0'  # Replace with your Arduino's port if needed
arduino_available = True

try:
    board = Arduino(port)
except Exception as e:
    print("Debug: No Arduino detected. Running in debug mode.", e)
    arduino_available = False
    board = None

# Define pins
PWM_PIN_3 = 3
PWM_PIN_5 = 5
PIN_8 = 8
PIN_10 = 10
PIN_9 = 9 #reverse direction
reverse_enabled = False

if arduino_available:
    # Start iterator thread so board reads continuously
    it = util.Iterator(board)
    it.start()
    # Enable analog reporting on pin A0 (first analog input)
    board.analog[0].enable_reporting()

    # Set digital pin modes
    board.digital[PWM_PIN_3].mode = PWM
    board.digital[PWM_PIN_5].mode = PWM
    board.digital[PIN_8].mode = OUTPUT
    board.digital[PIN_10].mode = OUTPUT
    board.digital[PIN_9].mode = OUTPUT 
    board.digital[PIN_9].write(0) 
    
# Set PWM function with conditional execution
def set_pwm(pin, duty_cycle):
    if arduino_available:
        scaled_duty_cycle = duty_cycle / 255
        board.digital[pin].write(scaled_duty_cycle)
    else:
        print(f"Debug: Arduino not available. Ignoring set_pwm for pin {pin} with duty cycle {duty_cycle}.")

# Functions to control motors using sliders
def update_motor_3(value):
    set_pwm(PWM_PIN_3, int(value))

def update_motor_5(value):
    set_pwm(PWM_PIN_5, int(value))

# Functions for pins 8 and 10 (control digital output with debug messages if no board)
def control_pin_8(state):
    if arduino_available:
        board.digital[PIN_8].write(int(state))
    else:
        print(f"Debug: Arduino not available. Ignoring control_pin_8 for state {state}.")

def control_pin_10(state):
    if arduino_available:
        board.digital[PIN_10].write(int(state))
    else:
        print(f"Debug: Arduino not available. Ignoring control_pin_10 for state {state}.")

# NEW: Callback function for analog pin A0
def handle_A0_change(value):
    if value is not None:
        scaled_value = int(value * 1023)  # Scale from 0-1 to 0-1023
        analog_label.config(text=f"A0 Value: {scaled_value}")
    else:
        analog_label.config(text="A0 Value: Waiting for value...")

# Register callback for analog pin A0
if arduino_available:
    board.analog[0].register_callback(handle_A0_change)

# Reverse button function 
def toggle_reverse_direction():
    global reverse_enabled
    reverse_enabled = not reverse_enabled
    state = 1 if reverse_enabled else 0
    if arduino_available:
        board.digital[PIN_9].write(state)
    print(f"Debug: Reverse Direction {'ON' if state else 'OFF'}")
    reverse_button.config(text=f"Reverse {'ON' if state else 'OFF'}")

# Function to reset the Arduino connection
def reset_arduino():
    global board, arduino_available
    try:
        board = Arduino(port)
        arduino_available = True
        # Restart the iterator and reinitialize pin modes and analog reporting for A0
        it = util.Iterator(board)
        it.start()
        board.digital[PWM_PIN_3].mode = PWM
        board.digital[PWM_PIN_5].mode = PWM
        board.digital[PIN_8].mode = OUTPUT
        board.digital[PIN_10].mode = OUTPUT
        board.digital[PIN_9].mode = OUTPUT
        board.digital[PIN_9].write(0) 
        board.analog[0].enable_reporting()
        board.analog[0].register_callback(handle_A0_change)
        print("Arduino connection reset successfully.")
    except Exception as e:
        print("Debug: Unable to reset Arduino connection. Still running in debug mode.", e)
        arduino_available = False

# Setup GUI
window = tk.Tk()
window.title("BLDC Motor Control")

frame = tk.Frame(window)
frame.pack(padx=10, pady=10)

# Slider for Motor on Pin 3
slider_motor_3 = tk.Scale(
    frame,
    from_=0,
    to=255,
    resolution=1,
    orient=tk.HORIZONTAL,
    label="Motor Speed (Pin 3)",
    command=update_motor_3,
    length=400,
    sliderlength=45,  
    width=35,
)
slider_motor_3.grid(row=0, column=0, padx=5, pady=5)

# Slider for Motor on Pin 5
slider_motor_5 = tk.Scale(
    frame,
    from_=0,
    to=255,
    resolution=1,
    orient=tk.HORIZONTAL,
    label="Motor Speed (Pin 5)",
    command=update_motor_5,
    length=400,
    sliderlength=45,  
    width=35,
)
slider_motor_5.grid(row=1, column=0, padx=5, pady=5)

# Toggle buttons for pins 8 and 10
button_pin_8_on = tk.Button(frame, text="Pin 8 ON", command=lambda: control_pin_8(1))
button_pin_8_on.grid(row=2, column=0, padx=5, pady=5)

button_pin_8_off = tk.Button(frame, text="Pin 8 OFF", command=lambda: control_pin_8(0))
button_pin_8_off.grid(row=2, column=1, padx=5, pady=5)

button_pin_10_on = tk.Button(frame, text="Pin 10 ON", command=lambda: control_pin_10(1))
button_pin_10_on.grid(row=3, column=0, padx=5, pady=5)

button_pin_10_off = tk.Button(frame, text="Pin 10 OFF", command=lambda: control_pin_10(0))
button_pin_10_off.grid(row=3, column=1, padx=5, pady=5)

# Reset button to reconnect to the Arduino after unplugging/re-plugging
reset_button = tk.Button(frame, text="Reconnect Arduino", command=reset_arduino)
reset_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

# Label to display analog reading from A0
analog_label = tk.Label(frame, text="A0 Value: N/A")
analog_label.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

#reverse button
reverse_button = tk.Button(frame, text="Reverse OFF", command=toggle_reverse_direction)
reverse_button.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

# Start the GUI event loop
window.mainloop()
