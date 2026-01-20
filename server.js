const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Enable CORS
app.use(cors());

// Serve static files from the current directory
app.use(express.static(__dirname));

const API_TOKEN = '7407~YHY2DTA7GtKKZBeBE3UB9UM8Y6rtMeCARvhQ4CzeuAwm9u4wW6ARJREWQNFmVBHy';
const BASE_URL = 'https://byu.instructure.com/api/v1';

// Proxy endpoint for courses
app.get('/api/courses', async (req, res) => {
  try {
    const response = await fetch(`${BASE_URL}/courses?enrollment_state=active`, {
      headers: { 'Authorization': `Bearer ${API_TOKEN}` }
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

// Proxy endpoint for assignments
app.get('/api/courses/:courseId/assignments', async (req, res) => {
  try {
    const { courseId } = req.params;
    const response = await fetch(
      `${BASE_URL}/courses/${courseId}/assignments?bucket=upcoming&per_page=15`,
      { headers: { 'Authorization': `Bearer ${API_TOKEN}` } }
    );
    const data = await response.json();
    res.json(data);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
