const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');  // Import the cors package

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let currentSum = 0; // Initialize the current sum

app.use(express.json());
app.use(cors()); // Enable CORS for all routes

// Serve static files from the React app
app.use(express.static('client/build'));

// REST endpoint to add a number
app.post('/add', (req, res) => {
    const { number } = req.body;
    currentSum += number;
    broadcast({ sum: currentSum });
    res.json({ sum: currentSum });
});

// REST endpoint to reset the sum
app.post('/reset', (req, res) => {
    currentSum = 0;
    broadcast({ sum: currentSum });
    res.json({ sum: currentSum });
});

// Broadcast function to send messages to all clients
function broadcast(data) {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
        }
    });
}

// WebSocket connection
wss.on('connection', (ws) => {
    console.log('Client connected');
    
    // Send the current sum to the newly connected client
    ws.send(JSON.stringify({ sum: currentSum }));

    ws.on('message', (message) => {
        console.log(`Received message => ${message}`);
        try {
            const data = JSON.parse(message);
            if (data.type === 'add') {
                currentSum += data.number; // Add the received number to the current sum
            } else if (data.type === 'reset') {
                currentSum = 0; // Reset the current sum
            }
            const response = { sum: currentSum, timestamp: data.timestamp };
            broadcast(response); // Broadcast the updated sum and original timestamp to all clients
        } catch (error) {
            console.error('Error processing message', error);
        }
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
