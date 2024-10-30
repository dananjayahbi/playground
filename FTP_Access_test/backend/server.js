const express = require('express');
const ftp = require('basic-ftp');
const cors = require('cors');
const path = require('path'); // To handle file paths

//.env
require('dotenv').config();

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

// FTP client function to connect, navigate directories, list files, and download files
async function connectToFTP() {
  const client = new ftp.Client();
  client.ftp.verbose = true;  // Enable detailed logging

  try {
    // Connect to the FTP server using the provided credentials
    await client.access({
      host: process.env.HOST, // FTP host
      user: process.env.USER,  // FTP username
      password: process.env.PASSWORD,  // FTP password
      secure: false,  // Disable FTPS for free-tier accounts
    });

    // Log the current directory
    const currentDir = await client.pwd();
    console.log(`Current directory: ${currentDir}`);

    // Navigate to the parent directory ("..")
    console.log('Trying to change to the parent directory (..)');
    await client.cd('..');  // Change to the parent directory

    // Log success and the new current directory
    const newDir = await client.pwd();
    console.log(`Changed to parent directory. New current directory: ${newDir}`);

    // Now, attempt to list the files in the current directory
    console.log('Listing files in the current directory...');
    const fileList = await client.list();  // List files in the current directory

    console.log('Files in the directory:');
    fileList.forEach(file => {
      console.log(`${file.name} (${file.type === 1 ? 'Directory' : 'File'})`);
    });

    // Define the target file
    const targetFile = "testImg.jpg";

    // Find the target file in the directory list
    const file = fileList.find(f => f.name === targetFile);

    if (file) { // Check if the file is found, regardless of type
      const localFilePath = path.join(__dirname, file.name);  // Local file path to save
      console.log(`Downloading file: ${file.name} to ${localFilePath}`);
      await client.downloadTo(localFilePath, file.name);  // Download the file
      console.log(`File downloaded successfully: ${file.name}`);
    } else {
      console.log(`File ${targetFile} not found.`);
    }

  } catch (error) {
    console.error('Error during FTP operation:', error);
  } finally {
    client.close();
  }
}

// Endpoint to trigger the FTP connection and file operations
app.get('/connect-ftp', async (req, res) => {
  try {
    await connectToFTP();
    res.json({ message: 'FTP connection and file operations attempted, check console for results.' });
  } catch (error) {
    res.status(500).json({ error: 'FTP connection failed' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});


/* ................
Use "http://localhost:5000/connect-ftp" URL to trigger the FTP connection and file operations. This will log the current directory, 
navigate to the parent directory, list the files in the directory, and attempt to download a specific file (testImg.jpg) if found.
*/