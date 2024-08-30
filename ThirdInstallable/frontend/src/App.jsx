import { useState } from 'react';
import './App.css';

function App() {
  const [number, setNumber] = useState(null);
  const [errorLog, setErrorLog] = useState(null);

  const fetchRandomNumber = async () => {
    try {
      const response = await fetch('http://localhost:3001/random');
      if (!response.ok) {
        setErrorLog(`Server error: ${response.status}`);
      }
      const data = await response.json();
      setNumber(data.number);
    } catch (error) {
      console.error('Error fetching random number:', error);
      setErrorLog(`Server error`);
    }
  };
  

  return (
    <div className="App">
      <button onClick={fetchRandomNumber}>Click Me</button>
      {number !== null && <p>Random Number: {number}</p>} <br />
      {errorLog && <p>{errorLog}</p>}
    </div>
  );
}

export default App;
