import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [numRequests, setNumRequests] = useState(10);
    const [responseTimes, setResponseTimes] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleStressTest = async () => {
        setLoading(true);
        setResponseTimes([]);
        const requests = [];
        
        for (let i = 0; i < numRequests; i++) {
            const startTime = Date.now();
            requests.push(
                axios.get('http://localhost:5000/api/test')
                    .then(response => {
                        const endTime = Date.now();
                        return endTime - startTime;
                    })
                    .catch(err => {
                        console.error('Request failed', err);
                        return null;
                    })
            );
        }

        const results = await Promise.all(requests);
        setResponseTimes(results.filter(time => time !== null));
        setLoading(false);
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Stress Test Endpoint</h1>
            <div>
                <label>Number of Requests: </label>
                <input
                    type="number"
                    value={numRequests}
                    onChange={(e) => setNumRequests(e.target.value)}
                    min="1"
                />
            </div>
            <button onClick={handleStressTest} disabled={loading}>
                {loading ? 'Testing...' : 'Start Stress Test'}
            </button>

            {responseTimes.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                    <h2>Results</h2>
                    <p>Average Response Time: {(
                        responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
                    ).toFixed(2)} ms</p>
                    <p>Number of Successful Requests: {responseTimes.length}</p>
                </div>
            )}
        </div>
    );
}

export default App;
