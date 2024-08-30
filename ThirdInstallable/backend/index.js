const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Endpoint to generate a random number
app.get('/random', (req, res) => {
    const randomNumber = Math.floor(Math.random() * 1001);
    res.json({ number: randomNumber });
});

// Serve static files from the frontend build
app.use(express.static(path.join(__dirname, '../frontend/dist')));

app.listen(PORT, () => {
    console.log(`Backend server running on http://localhost:${PORT}`);
});
