const express = require('express');
const cors = require('cors'); // Import cors
const app = express();
const PORT = 5000;

// Enable CORS for all routes
app.use(cors());

app.get('/api/test', (req, res) => {
    // Do some heavy computation
    const start = Date.now();
    while (Date.now() - start < 2000) {}
    res.send('Done');
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
