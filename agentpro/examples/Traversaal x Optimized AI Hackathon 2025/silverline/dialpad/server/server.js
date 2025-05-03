// server/server.js
require('dotenv').config();
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const morgan = require('morgan');
const twilio = require('twilio');

const AccessToken = twilio.jwt.AccessToken;
const VoiceGrant = AccessToken.VoiceGrant;

const app = express();
const port = process.env.PORT || 3001;

// Use morgan to log incoming requests
app.use(morgan('dev'));

// Parse incoming POST data from Twilio
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json()); // Add support for JSON bodies as well

// Serve static files from the public folder
app.use(express.static(path.join(__dirname, '../public')));

// Serve the dialer application at the root URL
app.get('/dialer', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/dialer/index.html'));
});

// Endpoint to generate a Twilio Access Token
app.get('/dialer/token', (req, res) => {
  console.log('GET /dialer/token requested');
  try {
    const voiceGrant = new VoiceGrant({
      outgoingApplicationSid: process.env.TWILIO_TWIML_APP_SID,
    });

    const token = new AccessToken(
      process.env.TWILIO_ACCOUNT_SID,
      process.env.TWILIO_API_KEY,
      process.env.TWILIO_API_SECRET,
      { identity: 'user_' + Math.random().toString(36).substr(2, 8) }
    );

    token.addGrant(voiceGrant);
    console.log('Token generated successfully');
    res.send({ token: token.toJwt() });
  } catch (err) {
    console.error('Error generating token:', err);
    res.status(500).send({ error: err.message });
  }
});

// Outbound voice endpoint for Twilio Client calls with valid callerId
app.post('/dialer/voice-outbound', (req, res) => {
  console.log('POST /dialer/voice-outbound requested with body:', req.body);
  
  // Retrieve the target number from the POST body; use default if not provided
  const targetNumber = req.body.number || '+19472822980';
  console.log('Dialing number:', targetNumber);

  // Use a valid callerId (must be a Twilio number or a verified outgoing caller ID)
  const callerId = process.env.VALID_CALLER_ID || '+12345678901'; // Replace with your valid number

  const twiml = new twilio.twiml.VoiceResponse();
  
  try {
    const dial = twiml.dial({ callerId: callerId });
    dial.number(targetNumber);

    console.log('Sending TwiML response:', twiml.toString());
    res.type('text/xml');
    res.send(twiml.toString());
  } catch (error) {
    console.error('Error generating TwiML:', error);
    twiml.say('An error occurred while processing your call. Please try again later.');
    res.type('text/xml');
    res.send(twiml.toString());
  }
});

// Debug endpoint to check Twilio configuration
app.get('/dialer/debug', async (req, res) => {
  if (!process.env.TWILIO_ACCOUNT_SID || !process.env.TWILIO_AUTH_TOKEN) {
    return res.status(500).json({ error: 'Twilio credentials not configured' });
  }

  try {
    const twilioClient = twilio(
      process.env.TWILIO_ACCOUNT_SID,
      process.env.TWILIO_AUTH_TOKEN
    );
    
    // Check if the application exists
    const app = await twilioClient.applications(process.env.TWILIO_TWIML_APP_SID).fetch();
    
    // Return configuration info
    res.json({
      success: true,
      appSid: app.sid,
      voiceUrl: app.voiceUrl,
      voiceMethod: app.voiceMethod,
      friendlyName: app.friendlyName,
      serverUrl: `http://localhost:${port}`,
      requiredVoiceUrl: `http://localhost:${port}/dialer/voice-outbound`
    });
  } catch (error) {
    console.error('Debug error:', error);
    res.status(500).json({
      error: error.message,
      suggestion: 'Make sure your Twilio application is properly configured. The Voice URL should point to your server /dialer/voice-outbound endpoint.'
    });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
