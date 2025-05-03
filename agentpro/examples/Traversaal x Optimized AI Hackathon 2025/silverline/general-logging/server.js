// server.js
const express = require('express');
const path = require('path');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3002;

// Use morgan to log incoming requests
app.use(morgan('dev'));

// Serve static files from the current directory using the /gen-log prefix
app.use('/gen-log', express.static(path.join(__dirname)));

// Default route to redirect to /gen-log
// app.get('/', (req, res) => {
//   res.redirect('/gen-log');
// });

app.get('/gen-log/env', (req, res) => {
  const environment = {
    AI_BACKEND_API: process.env.AI_BACKEND_API,
    BACKEND_API: process.env.BACKEND_API,
    FRONTEND_API: process.env.FRONTEND_API
  }
  res.json(environment);
});

app.listen(port, () => {
  console.log(`General Logging server is running on http://localhost:${port}/gen-log`);
}); 

