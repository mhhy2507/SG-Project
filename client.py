import socketio
import requests

# Connect to the server
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to server')

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

@sio.on('response')
def on_response(data):
    print('Server response:', data)

def move(direction):
    sio.emit('move', {'direction': direction})

def capture_image():
    response = requests.get('http://localhost:5000/capture')
    if response.status_code == 200:
        with open('captured_image.jpg', 'wb') as f:
            f.write(response.content)
        print('Image captured successfully')
    else:
        print('Failed to capture image')

if __name__ == "__main__":
    # Connect to the server
    sio.connect('http://localhost:5000')

    while True:
        command = input('Enter command (up, down, left, right, capture, exit): ')
        if command == 'exit':
            break
        elif command in ['up', 'down', 'left', 'right']:
            move(command)
        elif command == 'capture':
            capture_image()

    # Disconnect from the server
    sio.disconnect()
