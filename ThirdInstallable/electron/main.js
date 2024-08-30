const { app, BrowserWindow } = require('electron');
const path = require('path');
const express = require('express');

const server = express();
const PORT = 3001;

// Serve static files from the frontend build
const frontendDistPath = path.join(__dirname, 'resources', 'frontend', 'dist');
server.use(express.static(frontendDistPath));

// Ensure API routes are handled before static files
server.get('/random', (req, res) => {
  const randomNumber = Math.floor(Math.random() * 1001);
  res.json({ number: randomNumber });
});

// Serve index.html for all other routes
server.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/dist', 'index.html'));
});

server.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false
    },
    autoHideMenuBar: true, // Hides the menu bar by default
    // titleBarStyle: 'hidden' // Optional: Hides the title bar as well
  });

  mainWindow.loadURL(`http://localhost:${PORT}`);
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
