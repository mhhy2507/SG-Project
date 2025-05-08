// Connect to the Socket.IO server
var socket = io.connect('http://192.168.1.84:5000');
var maintainingSpeed = false;
var speed = 0;
var speedTimeout;
var speedInterval;
var speedDecreaseInterval;

function toggleButton(buttonId) {
  var button = document.getElementById(buttonId);
  var active = false;
  
  button.addEventListener('click', function() {
    active = !active;
    button.style.backgroundColor = active ? 'red' : '';
    
    if (buttonId === 'up_btn') {
      if (active) {
        clearInterval(speedDecreaseInterval);
        speedInterval = setInterval(function() {
          speed = Math.min(100, speed + 1);
          updateSpeedBar();
          resetSpeedTimeout();
        }, 100);
      } else {
        clearInterval(speedInterval);
      }
    } else if (buttonId === 'down_btn') {
      if (active) {
        clearInterval(speedDecreaseInterval);
        speedInterval = setInterval(function() {
          speed = Math.max(0, speed - 1);
          updateSpeedBar();
          resetSpeedTimeout();
        }, 100);
      } else {
        clearInterval(speedInterval);
      }
    } else if (buttonId === 'left_btn') {
      if (active) {
        console.log("[DEBUG] Left toggle activated");
        socket.emit('move', { direction: 'left', state: 'start' });
      } else {
        console.log("[DEBUG] Left toggle deactivated");
        socket.emit('move', { direction: 'left', state: 'stop' });
      }
    } else if (buttonId === 'right_btn') {
      if (active) {
        console.log("[DEBUG] Right toggle activated");
        socket.emit('move', { direction: 'right', state: 'start' });
      } else {
        console.log("[DEBUG] Right toggle deactivated");
        socket.emit('move', { direction: 'right', state: 'stop' });
      }
    } else if (buttonId === 'speed_button') {
      maintainingSpeed = !maintainingSpeed;
      button.style.backgroundColor = maintainingSpeed ? '#28a745' : '#007bff';
      if (maintainingSpeed) {
        clearInterval(speedDecreaseInterval);
      } else {
        resetSpeedTimeout();
      }
    }
  });
}

// Initialize all the toggle buttons
toggleButton('up_btn');
toggleButton('down_btn');
toggleButton('left_btn');
toggleButton('right_btn');
toggleButton('speed_button');

function updateSpeedBar() {
  document.getElementById('speed_progress').style.height = (speed / 100 * 90 + 10) + '%';
  document.getElementById('speed_progress').innerText = 'Speed: ' + speed;
  console.log('[DEBUG] Sending speed:', speed);
  socket.emit('speed_change', { speed: speed });
}

// Emit initial speed
socket.emit('speed_change', { speed: speed });
console.log('[DEBUG] Emitting speed:', speed);

function resetSpeedTimeout() {
  clearTimeout(speedTimeout);
  speedTimeout = setTimeout(function() {
    if (!maintainingSpeed) {
      speedDecreaseInterval = setInterval(function() {
        if (speed > 0) {
          speed = Math.max(0, speed - 1);
          updateSpeedBar();
        } else {
          clearInterval(speedDecreaseInterval);
        }
      }, 100);
    }
  }, 2000);
}

// Capture image functionality
document.getElementById('capture_btn').addEventListener('click', function() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/capture', true);
  xhr.responseType = 'blob';
  xhr.onload = function() {
    if (this.status === 200) {
      var blob = this.response;
      var img = document.createElement('img');
      img.onload = function() {
        window.URL.revokeObjectURL(img.src);
      };
      img.src = window.URL.createObjectURL(blob);
      document.body.appendChild(img);
    }
  };
  xhr.send();
});

// Socket response event
socket.on('response', function(msg) {
  console.log(msg.data);
});

// Fetch the video feed
fetch('/video_feed')
  .then(response => {
    if (response.status === 200) {
      document.getElementById('video_feed').innerHTML = '<img src="/video_feed" alt="Video Feed">';
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Speed bar dragging functionality
var speedBar = document.getElementById('speed_bar');
var speedProgress = document.getElementById('speed_progress');
var isDragging = false;

speedProgress.addEventListener('mousedown', function(e) {
  isDragging = true;
  document.body.style.userSelect = 'none';
});

document.addEventListener('mouseup', function() {
  isDragging = false;
  document.body.style.userSelect = '';
});

document.addEventListener('mousemove', function(e) {
  if (isDragging) {
    var barRect = speedBar.getBoundingClientRect();
    var newHeight = Math.max(0, Math.min(100, ((barRect.bottom - e.clientY) / barRect.height) * 100));
    speed = Math.round(newHeight * (100 / 90));
    updateSpeedBar();
    resetSpeedTimeout();
  }
});

speedProgress.addEventListener('touchstart', function(e) {
  isDragging = true;
  document.body.style.userSelect = 'none';
  e.preventDefault();
});

document.addEventListener('touchend', function(e) {
  isDragging = false;
  document.body.style.userSelect = '';
  e.preventDefault();
});

document.addEventListener('touchmove', function(e) {
  if (isDragging) {
    var touch = e.touches[0];
    var barRect = speedBar.getBoundingClientRect();
    var newHeight = Math.max(0, Math.min(100, ((barRect.bottom - touch.clientY) / barRect.height) * 100));
    speed = Math.round(newHeight * (100 / 90));
    updateSpeedBar();
    resetSpeedTimeout();
    e.preventDefault();
  }
});

updateSpeedBar();
resetSpeedTimeout();
