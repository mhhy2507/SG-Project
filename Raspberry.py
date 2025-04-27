import gc
import cv2
import requests
import time
import socketio
import threading
from pyfirmata2 import Arduino, util

# URL of the Flask server endpoint
url = 'http://192.168.1.84:5000/upload_frame'

# Setup Arduino with Firmata
try:
    board = Arduino('COM6')  # /dev/ttyUSB0
    it = util.Iterator(board)
    it.start()
    time.sleep(2)  # Allow time for Arduino initialization

    pul_pin = board.get_pin('d:10:o')
    dir_pin = board.get_pin('d:8:o')
    pwmPin1 = board.get_pin('d:3:p')
    pwmPin2 = board.get_pin('d:5:p')
    print("[INFO] Arduino connected successfully")
except Exception as e:
    print(f"[ERROR] Arduino not connected: {e}")
    board = None
    pul_pin = dir_pin = pwmPin1 = pwmPin2 = None

# Camera Setup
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Camera could not be opened")
    print("[INFO] Camera connected successfully")
except Exception as e:
    print(f"[ERROR] Camera not connected: {e}")
    cap = None

# SocketIO Setup
sio = socketio.Client()

speed = 0
latest_frame = None
running = True

motor_moving = False

def continuous_move(direction):
    global motor_moving
    motor_moving = True
    print(f"[DEBUG] Starting continuous movement: {direction}")
    while motor_moving:
        if direction == 'left':
            stepper_motor_control("LEFT")
        elif direction == 'right':
            stepper_motor_control("RIGHT")
        time.sleep(0.01)
    print(f"[DEBUG] Exiting continuous movement loop for: {direction}")

def stepper_motor_control(direction):
    if not pul_pin or not dir_pin:
        print("[WARNING] Arduino pins not initialized; skipping motor control")
        return

    if direction == "LEFT":
        dir_pin.write(1)  # Set direction to left
    elif direction == "RIGHT":
        dir_pin.write(0)  # Set direction to right

    for i in range(1000):  # Adjust steps if needed
        if not motor_moving:
            print("[DEBUG] Breaking pulse loop early due to stop command")
            break
        pul_pin.write(1)
        time.sleep(0.001)
        pul_pin.write(0)
        time.sleep(0.001)


def control_motors():
    global speed
    pwm_value = speed / 100  # Normalize to 0-1
    pwm_value = max(0, min(1, pwm_value))
    print(f"[DEBUG] Writing PWM - Pin 9: {pwm_value}, Pin 10: {pwm_value}")
    pwmPin1.write(pwm_value)
    pwmPin2.write(pwm_value)
    if pwm_value == 0:
        print("[INFO] Stopping motor with PWM")

@sio.event
def connect():
    print("Connected to Flask server")

@sio.event
def disconnect():
    print("Disconnected from Flask server")

@sio.on('update_speed')
def on_speed_change(data):
    global speed
    print(f"[DEBUG] Received speed change event: {data}")
    if 'speed' in data:
        new_speed = int(data['speed'])
        if new_speed != speed:
            speed = new_speed
            print(f"[DEBUG] Updated speed to: {speed}")
            control_motors()
        else:
            print(f"[DEBUG] Speed unchanged: {speed}")
    elif 'direction' in data:
        direction = data['direction']
        if direction in ["LEFT", "RIGHT"]:
            print(f"[DEBUG] Moving {direction}")
            stepper_motor_control(direction)
        else:
            print(f"[ERROR] Invalid direction: {direction}")
    else:
        print("[ERROR] No valid key (speed or direction) in data")

@sio.on('update_direction')
def on_direction_change(data):
    global motor_moving
    if 'direction' in data and 'state' in data:
        direction = data['direction']
        state = data['state']
        print(f"[DEBUG] Received move command: {direction} - {state}")
        if state == 'start':
            if not motor_moving:
                threading.Thread(target=continuous_move, args=(direction,)).start()
        elif state == 'stop':
            motor_moving = False
            print(f"[INFO] Stopping movement {direction}")

def capture_and_upload_frames():
    global latest_frame, running
    if not cap:
        print("[WARNING] Camera not available; skipping frame capture")
        return

    while running:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame")
            continue
        latest_frame = frame
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("[ERROR] Failed to encode frame")
            continue
        frame_bytes = buffer.tobytes()
        try:
            response = requests.post(url, files={'frame': frame_bytes})
            if response.status_code != 200:
                print(f"[ERROR] Failed to send frame: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
        gc.collect()
        time.sleep(0.1)
    cap.release()
    print("[INFO] Camera capture stopped.")


def start_socket_io():
    sio.connect('http://192.168.1.84:5000')
    while running:
        sio.sleep(1)

socket_thread = threading.Thread(target=start_socket_io)
video_thread = threading.Thread(target=capture_and_upload_frames)

socket_thread.start()
video_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("[INFO] Exiting...")
finally:
    running = False
    socket_thread.join()
    video_thread.join()
    sio.disconnect()
    print("[INFO] Cleanup complete.")
