from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import numpy as np
import threading
import time
import logging

# Suppress Flask's request logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
thread = None
thread_lock = threading.Lock()
CORS(app)

latest_frame = None
frame_lock = threading.Lock()  # Lock for frame access

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    global latest_frame
    if 'frame' not in request.files:
        return 'No frame found', 400

    frame = request.files['frame'].read()
    frame_np = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
    
    with frame_lock:  # Safely update the latest frame
        latest_frame = frame_np

    return 'Frame received', 200

@socketio.on('speed_change')
def handle_speed_change(data):
    print('Speed change:', data)
    socketio.emit('update_speed', data)

@socketio.on('move')
def handle_move(data):
    print(f"[DEBUG] Move command received: {data}")  # Debugging output
    socketio.emit('update_direction', data)  # Send move command to the client

def gen():
    global latest_frame
    while True:
        with frame_lock:  # Safely access the latest frame
            if latest_frame is not None:
                ret, buffer = cv2.imencode('.jpg', latest_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')

        time.sleep(0.1)  # Avoid busy waiting

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
