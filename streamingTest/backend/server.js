const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware to serve static files
app.use(express.static('client/build'));

// Video streaming endpoint
app.get('/video', (req, res) => {
    const filePath = path.join(__dirname, 'Assets', 'v1.mp4');
    const stat = fs.statSync(filePath);
    const fileSize = stat.size;
    const range = req.headers.range;

    if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = Math.min(fileSize - 1, parseInt(parts[1], 10) || fileSize - 1);

        const contentLength = (end - start) + 1;
        const headers = {
            "Content-Range": `bytes ${start}-${end}/${fileSize}`,
            "Accept-Ranges": "bytes",
            "Content-Length": contentLength,
            "Content-Type": "video/mp4"
        };

        res.writeHead(206, headers);
        const stream = fs.createReadStream(filePath, { start, end });
        stream.pipe(res);
    } else {
        const headers = {
            "Content-Length": fileSize,
            "Content-Type": "video/mp4"
        };

        res.writeHead(200, headers);
        fs.createReadStream(filePath).pipe(res);
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
