// public/js/main.js
let device;

function updateStatus(message) {
  document.getElementById('status').innerText = message;
  console.log('Status:', message);
}

function setupTwilioDevice(token) {
  console.log('Setting up Twilio Device with token:', token);
  
  // Initialize device with better error handling and debug options
  device = new Twilio.Device(token, {
    codecPreferences: ['opus', 'pcmu'],
    fakeLocalDTMF: true,
    enableRingingState: true,
    debug: true // Enable debug mode to get more detailed logs
  });

  // Log capabilities of the device for debugging
  device.on('registered', function() {
    console.log('Twilio.Device registered!');
  });

  device.on('ready', () => {
    updateStatus('Ready to make calls');
    console.log('Twilio Device is ready');
  });
  device.on('error', (error) => {
    updateStatus('Error: ' + error.message);
    console.error('Twilio Device Error:', error);
  });
  device.on('connect', () => {
    updateStatus('Call in progress...');
    console.log('Call connected');
    document.getElementById('callButton').disabled = true;
    document.getElementById('hangupButton').disabled = false;
  });
  device.on('disconnect', () => {
    updateStatus('Call ended.');
    console.log('Call disconnected');
    document.getElementById('callButton').disabled = false;
    document.getElementById('hangupButton').disabled = true;
  });
}

function fetchToken() {
  console.log('Fetching token...');
  fetch('/dialer/token')
    .then(response => response.json())
    .then(data => {
      console.log('Token received:', data.token);
      setupTwilioDevice(data.token);
    })
    .catch(error => {
      updateStatus('Could not get a token from server.');
      console.error('Error fetching token:', error);
    });
}

// Function to make a call after ensuring AudioContext is running
async function makeCall(phoneNumber) {
  if (!device) {
    console.error('Twilio Device not ready');
    return;
  }

  // Make sure AudioContext is running before making the call
  if (device.audio && device.audio.audioContext && device.audio.audioContext.state !== 'running') {
    try {
      await device.audio.audioContext.resume();
      console.log('AudioContext started successfully');
    } catch (error) {
      console.error('Failed to start AudioContext:', error);
      updateStatus('Error starting audio. Please try again.');
      return;
    }
  }

  // Now that AudioContext is running, make the call
  try {
    // Connect with parameters for the voice-outbound endpoint
    const params = {
      // This should match the parameter name expected in your server's voice-outbound endpoint
      number: phoneNumber
    };
    
    const call = device.connect(params);
    
    // Add call-specific event listeners
    call.on('warning', warning => {
      console.warn('Call warning:', warning.name, warning.message);
    });
    
    call.on('error', error => {
      console.error('Call connection error:', error.message);
      updateStatus('Call error: ' + error.message);
    });
    
    updateStatus('Calling ' + phoneNumber + '...');
  } catch (error) {
    console.error('Error connecting call:', error);
    updateStatus('Error connecting: ' + error.message);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM fully loaded, fetching token...');
  fetchToken();

  // Add click listeners to keypad digits to append to phone input
  const digitButtons = document.querySelectorAll('.digit');
  digitButtons.forEach(button => {
    button.addEventListener('click', () => {
      const phoneInput = document.getElementById('phoneNumber');
      phoneInput.value += button.innerText;
      console.log('Keypad button pressed:', button.innerText, 'New number:', phoneInput.value);
    });
  });

  // When the Call button is clicked, connect via Twilio
  document.getElementById('callButton').addEventListener('click', () => {
    const phoneNumber = document.getElementById('phoneNumber').value;
    console.log('Call button clicked, number:', phoneNumber);
    makeCall(phoneNumber);
  });

  // When the Hang Up button is clicked, disconnect the call
  document.getElementById('hangupButton').addEventListener('click', () => {
    console.log('Hang Up button clicked');
    if (device) {
      device.disconnectAll();
      updateStatus('Call ended.');
    }
  });
});
