import tkinter as tk
from pyfirmata2 import Arduino, OUTPUT, PWM, util
import time

print('hello')

# Set up the Arduino board with a try-except block
port = Arduino.AUTODETECT
arduino_available = True

try:
    board = Arduino(port) 
except Exception as e:
    print("Debug: No Arduino detected. Running in debug mode.", e)
    arduino_available = False
    board = None

# Define pins
PWM_PIN_3 = 3 #speed
PWM_PIN_5 = 5 #speed 
PIN_7 = 7 #turn 
PIN_6 = 6 #turn 
PIN_8 = 8 #dir
PIN_9 = 9 #dir
PIN_10 = 10 #dir 
PIN_11 = 11 #d

if arduino_available:
    it = util.Iterator(board)
    it.start()
    board.analog[0].enable_reporting()

    board.digital[PWM_PIN_3].mode = PWM
    board.digital[PWM_PIN_5].mode = PWM
    board.digital[PIN_7].mode = OUTPUT
    board.digital[PIN_6].mode = OUTPUT
    board.digital[PIN_8].mode = OUTPUT
    board.digital[PIN_9].mode = OUTPUT
    board.digital[PIN_10].mode = OUTPUT
    board.digital[PIN_11].mode = OUTPUT

def set_pwm(pin, duty_cycle):
    if arduino_available:
        scaled = duty_cycle / 255
        board.digital[pin].write(scaled)
    else:
        print(f"Debug: Ignoring set_pwm({pin}, {duty_cycle})")

def update_motor_3(value):
    set_pwm(PWM_PIN_3, int(value))

def update_motor_5(value):
    set_pwm(PWM_PIN_5, int(value))

def control_PIN_7(state):
    if arduino_available:
        board.digital[PIN_7].write(int(state))
    else:
        print(f"Debug: Ignoring control_PIN_7({state})")

def control_PIN_6(state):
    if arduino_available:
        board.digital[PIN_6].write(int(state))
    else:
        print(f"Debug: Ignoring control_PIN_6({state})")

def handle_A0_change(value):
    if value is not None:
        scaled = int(value * 1023)
        analog_label.config(text=f"A0 Value: {scaled}")
    else:
        analog_label.config(text="A0 Value: Waiting...")

def rotate_forward():
    if arduino_available:
        board.digital[PIN_10].write(1)
        board.digital[PIN_11].write(0)
        board.digital[PIN_8].write(1)
        board.digital[PIN_9].write(0)
    else:
        print("Debug: Simulating forward rotation.")

def rotate_reverse():
    if arduino_available:
        board.digital[PIN_10].write(0)
        board.digital[PIN_11].write(1)
        board.digital[PIN_8].write(0)
        board.digital[PIN_9].write(1)
    else:
        print("Debug: Simulating reverse rotation.")

if arduino_available:
    board.analog[0].register_callback(handle_A0_change)

def reset_arduino():
    global board, arduino_available
    try:
        board = Arduino(port)
        arduino_available = True
        it = util.Iterator(board)
        it.start()
        board.digital[PWM_PIN_3].mode = PWM
        board.digital[PWM_PIN_5].mode = PWM
        board.digital[PIN_7].mode = OUTPUT
        board.digital[PIN_6].mode = OUTPUT
        board.digital[PIN_8].mode = OUTPUT
        board.digital[PIN_9].mode = OUTPUT
        board.digital[PIN_10].mode = OUTPUT
        board.digital[PIN_11].mode = OUTPUT
        board.analog[0].enable_reporting()
        board.analog[0].register_callback(handle_A0_change)
        print("Arduino reconnected.")
    except Exception as e:
        print("Debug: Failed to reconnect Arduino.", e)
        arduino_available = False

# GUI
window = tk.Tk()
window.title("BLDC Motor Control")

frame = tk.Frame(window)
frame.pack(padx=10, pady=10)

slider_motor_3 = tk.Scale(
    frame, from_=0, to=255, resolution=1, orient=tk.HORIZONTAL,
    label="Motor Speed (Pin 3)", command=update_motor_3,
    length=400, sliderlength=45, width=35)
slider_motor_3.grid(row=0, column=0, padx=5, pady=5)

slider_motor_5 = tk.Scale(
    frame, from_=0, to=255, resolution=1, orient=tk.HORIZONTAL,
    label="Motor Speed (Pin 5)", command=update_motor_5,
    length=400, sliderlength=45, width=35)
slider_motor_5.grid(row=1, column=0, padx=5, pady=5)

button_PIN_7_on = tk.Button(frame, text="Pin 8 ON", command=lambda: control_PIN_7(1))
button_PIN_7_on.grid(row=2, column=0, padx=5, pady=5)

button_PIN_7_off = tk.Button(frame, text="Pin 8 OFF", command=lambda: control_PIN_7(0))
button_PIN_7_off.grid(row=2, column=1, padx=5, pady=5)

button_PIN_6_on = tk.Button(frame, text="Pin 10 ON", command=lambda: control_PIN_6(1))
button_PIN_6_on.grid(row=3, column=0, padx=5, pady=5)

button_PIN_6_off = tk.Button(frame, text="Pin 10 OFF", command=lambda: control_PIN_6(0))
button_PIN_6_off.grid(row=3, column=1, padx=5, pady=5)

reset_button = tk.Button(frame, text="Reconnect Arduino", command=reset_arduino)
reset_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

analog_label = tk.Label(frame, text="A0 Value: N/A")
analog_label.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

button_forward = tk.Button(frame, text="Forward", command=rotate_forward)
button_forward.grid(row=6, column=0, padx=5, pady=5)

button_reverse = tk.Button(frame, text="Backward", command=rotate_reverse)
button_reverse.grid(row=6, column=1, padx=5, pady=5)

window.mainloop()
