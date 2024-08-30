// App.jsx
import React from "react";

const App = () => {
  const handleDownload = () => {
    fetch("http://localhost:3001/download", {
      method: "GET",
    })
      .then((response) => response.blob())
      .then((blob) => {
        // Create a link element
        const link = document.createElement("a");
        // Create a URL for the blob and set it as the href attribute
        link.href = window.URL.createObjectURL(blob);
        // Set the download attribute to specify the filename
        link.download = "xyz.zip";
        // Append the link to the body
        document.body.appendChild(link);
        // Programmatically click the link to trigger the download
        link.click();
        // Remove the link from the document
        link.parentNode.removeChild(link);
      })
      .catch((err) => console.error("Download failed:", err));
  };

  return (
    <div>
      <button onClick={handleDownload}>Download xyz.zip</button>
    </div>
  );
};

export default App;
