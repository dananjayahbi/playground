import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
    // WebSocket states
    const [wsNumber, setWsNumber] = useState('');
    const [wsSum, setWsSum] = useState(0);
    const [wsRtt, setWsRtt] = useState(null);
    const ws = useRef(null);

    // REST API states
    const [apiNumber, setApiNumber] = useState('');
    const [apiSum, setApiSum] = useState(0);
    const [apiRtt, setApiRtt] = useState(null);

    useEffect(() => {
        ws.current = new WebSocket('ws://localhost:5000');

        ws.current.onopen = () => {
            console.log('WebSocket Client Connected');
        };

        ws.current.onmessage = (message) => {
            const data = JSON.parse(message.data);
            const endTime = Date.now();
            const startTime = data.timestamp;
            const roundTripTime = endTime - startTime;
            setWsSum(data.sum);
            setWsRtt(roundTripTime);
        };

        return () => {
            ws.current.close();
        };
    }, []);

    // WebSocket functions
    const sendWsNumber = () => {
        if (ws.current.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ type: 'add', number: Number(wsNumber), timestamp: Date.now() });
            ws.current.send(message);
            setWsNumber(''); // Clear the input field
        }
    };

    const resetWsSum = () => {
        if (ws.current.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ type: 'reset', timestamp: Date.now() });
            ws.current.send(message);
        }
    };

    // REST API functions
    const sendApiNumber = async () => {
        const startTime = Date.now();
        try {
            const response = await axios.post('http://localhost:5000/add', { number: Number(apiNumber) });
            const endTime = Date.now();
            const roundTripTime = endTime - startTime;
            setApiSum(response.data.sum);
            setApiRtt(roundTripTime);
            setApiNumber(''); // Clear the input field
        } catch (error) {
            console.error('Error sending number via API', error);
        }
    };

    const resetApiSum = async () => {
        const startTime = Date.now();
        try {
            const response = await axios.post('http://localhost:5000/reset');
            const endTime = Date.now();
            const roundTripTime = endTime - startTime;
            setApiSum(response.data.sum);
            setApiRtt(roundTripTime);
        } catch (error) {
            console.error('Error resetting sum via API', error);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Real-Time Sum Comparison</h1>
                <div className="container">
                    <div className="column">
                        <h2>WebSocket</h2>
                        <input 
                            type="number" 
                            value={wsNumber} 
                            onChange={(e) => setWsNumber(e.target.value)} 
                            placeholder="Enter a number"
                        />
                        <button onClick={sendWsNumber}>Send</button>
                        <button onClick={resetWsSum}>Reset</button>
                        <div>
                            <h3>Current Sum: {wsSum}</h3>
                            {wsRtt !== null && (
                                <p>Round-Trip Time: {wsRtt} ms</p>
                            )}
                        </div>
                    </div>
                    <div className="column">
                        <h2>REST API</h2>
                        <input 
                            type="number" 
                            value={apiNumber} 
                            onChange={(e) => setApiNumber(e.target.value)} 
                            placeholder="Enter a number"
                        />
                        <button onClick={sendApiNumber}>Send</button>
                        <button onClick={resetApiSum}>Reset</button>
                        <div>
                            <h3>Current Sum: {apiSum}</h3>
                            {apiRtt !== null && (
                                <p>Round-Trip Time: {apiRtt} ms</p>
                            )}
                        </div>
                    </div>
                </div>
            </header>
        </div>
    );
};

export default App;
