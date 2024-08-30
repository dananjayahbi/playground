const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for specific origin
const corsOptions = {
    origin: 'http://localhost:5173', // Update this to match your frontend origin
    optionsSuccessStatus: 200
};

app.use(cors(corsOptions));

// Path to the large zip file
const zipFilePath = path.join(__dirname, './assets', 'xyz.zip');

//.................................................................................................................
app.get('/download', (req, res) => {
    console.log('Download endpoint hit');
    console.log('Checking file existence at:', zipFilePath);
    if (fs.existsSync(zipFilePath)) {
        console.log('File exists, proceeding with download');
        res.setHeader('Content-Disposition', 'attachment; filename=xyz.zip');
        res.setHeader('Content-Type', 'application/zip');

        const fileStream = fs.createReadStream(zipFilePath);
        fileStream.pipe(res);
    } else {
        console.error('File not found:', zipFilePath);
        res.status(404).send('File not found');
    }
});
//.................................................................................................................

// app.get('/download', cors(corsOptions), (req, res) => {
//     console.log('Download endpoint hit');
//     console.log('Checking file existence at:', zipFilePath);
//     if (fs.existsSync(zipFilePath)) {
//         console.log('File exists, proceeding with download');
//         res.setHeader('Content-Disposition', 'attachment; filename=xyz.zip');
//         res.setHeader('Content-Type', 'application/zip');
//         res.setHeader('Access-Control-Allow-Origin', 'http://localhost:5173');
//         res.setHeader('Access-Control-Allow-Methods', 'GET');
//         res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

//         const fileStream = fs.createReadStream(zipFilePath);
//         fileStream.pipe(res);
//     } else {
//         console.error('File not found:', zipFilePath);
//         res.status(404).send('File not found');
//     }
// });


app.get('/test-cors', (req, res) => {
    res.json({ message: 'CORS is working' });
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
