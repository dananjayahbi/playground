import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const App = () => {
    const [bitrateBps, setBitrateBps] = useState(0); // State to hold bitrate in bits per second
    const [bitrateKbps, setBitrateKbps] = useState(0); // State to hold bitrate in kilobits per second
    const [bitrateMbps, setBitrateMbps] = useState(0); // State to hold bitrate in megabits per second
    const videoRef = useRef(null);

    useEffect(() => {
        const video = videoRef.current;
        let lastUpdateTime = Date.now();
        let lastLoadedBytes = 0;

        // Function to calculate and display bitrate
        const calculateBitrate = () => {
            const currentTime = Date.now();
            const loadedBytes = video.buffered.length > 0 ? video.buffered.end(video.buffered.length - 1) : 0;
            const elapsedTime = (currentTime - lastUpdateTime) / 1000; // Convert to seconds
            const bytesReceived = loadedBytes - lastLoadedBytes;

            if (elapsedTime > 0) {
                const bitrateBps = (bytesReceived * 8) / elapsedTime; // Bitrate in bits per second
                const bitrateKbps = bitrateBps / 1000; // Convert to kilobits per second
                const bitrateMbps = bitrateKbps / 1000; // Convert to megabits per second

                setBitrateBps(bitrateBps.toFixed(2));
                setBitrateKbps(bitrateKbps.toFixed(2));
                setBitrateMbps(bitrateMbps.toFixed(2));
            }

            lastUpdateTime = currentTime;
            lastLoadedBytes = loadedBytes;
        };

        // Set up the interval to calculate bitrate
        const interval = setInterval(calculateBitrate, 1000); // Update every second

        // Clean up the interval on component unmount
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <h1>Video Streaming with Bitrate Display</h1>
                <video
                    ref={videoRef}
                    controls
                    width="800"
                    height="450"
                    src="http://localhost:5000/video"
                    type="video/mp4"
                >
                    Your browser does not support the video tag.
                </video>
                <div>
                    <h3>Current Bitrate:</h3>
                    <p>{bitrateBps} bps | {bitrateKbps} KB/s | {bitrateMbps} MB/s</p>
                </div>
            </header>
        </div>
    );
};

export default App;
