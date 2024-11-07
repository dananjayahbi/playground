<div align="center">

# Image Background Remover

**A Image background remover tool created with rembg**

![main-image](https://i.pinimg.com/736x/2d/e9/e8/2de9e89dd18b3f1653bb49a7a4fb3ee4.jpg)

</div>

# Introduction

This project is a background removal application craeted as a hobby project that allows users to upload images, process them to remove backgrounds, and download the results. The application consists of two parts: <br>

<br>

- A **Flask backend** that handles image uploads, background removal, and file processing.

- A **React + Vite frontend** that provides a user-friendly interface for interacting with the application.

## Features

- Upload multiple images for background removal.
- Processed images are stored and served via a session-based system.
- Images can be downloaded or removed from the user interface.
- User functionalities

> <br>
>
> Since this is a hobby project and forcused only background removal, you may not meet best practices for some areas including:
>
> - Saving iamges in the backend instead of a cloud storage.
> - When user processed some images they can access those images (saved in the backend) by URLs and those URLs will be stored in the localstorage.
>   <br>

<div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
        <div>
            <img src="https://i.pinimg.com/736x/3f/3f/e2/3f3fe27dc6f25131f2943aa36a3d2853.jpg" alt="" style="width: 100%; max-width: 1000px;">
        </div>
        <div>
            <img src="https://i.pinimg.com/736x/2d/e9/e8/2de9e89dd18b3f1653bb49a7a4fb3ee4.jpg" alt="" style="width: 100%; max-width: 1000px;">
        </div>
        <div>
            <img src="https://i.pinimg.com/474x/c4/84/86/c484863e6318e633b167a947ea75d4a7.jpg" alt="" style="width: 100%; max-width: 1000px;">
        </div>
        <div>
            <img src="https://i.pinimg.com/474x/d1/3c/c9/d13cc9c17dd7e67250ad5122d9bdf2e0.jpg" alt="" style="width: 100%; max-width: 1000px;">
        </div>
        <div>
            <img src="https://i.pinimg.com/736x/bb/d5/f4/bbd5f41cd0f1d7fa5e3ff6446822f8e7.jpg" alt="" style="width: 100%; max-width: 1000px;">
        </div>
</div>

## Tech Stack

- Backend: Flask, Python, Rembg (for background removal)
- Frontend: React, Vite, Ant Design
- Storage: Local file system (Uploads/Outputs)
- Other: Multer for handling file uploads (in Node.js)

> I used "rembg" for remove backgrounds from images:
> [rembg](https://github.com/danielgatis/rembg)

## Pre-requirements

Before you begin, ensure you have the following installed on your machine:

- Python 3.x
- Node.js
- npm
- pip

# Installation

## Backend installation

1.  Clone the repository:

```bash
    git clone https://github.com/dananjayahbi/bg-remove-Flask-React-app.git
    cd bg-remove-Flask-React-app/backend
```

2.  Create a virtual environment and activate it:

```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3.  Install the required Python dependencies:

```bash
    pip install -r requirements.txt
```

4.  Setup environment variables

- Create a new file called **.env** at the root backend directory.
- Add the following environment variables:
  > MONGO_URI = (Your mongodb url)
  > SECRET_KEY = (JWT secret key)

> SECRET_EXAMPLE = 6Jc9da8Kfpx2YLSSeI6UJwp8q5EObZwcMfboV2uS1jxEZyDhaT3HFXNKm4et0dq

5.  Run the backend

```bash
    python3 app.py
```

## Frontend implementation

1.  Navigate to the frontend directory:

```bash
    git clone https://github.com/dananjayahbi/bg-remove-Flask-React-app.git
    cd bg-remove-Flask-React-app/backend
```

2.  Install the frontend dependencies:

```bash
    npm install
```

3.  Start the Vite development server:

```bash
    npm run dev
```

## Usage

1.  Upload images from the React frontend interface to the Flask backend.
2.  The backend will process the images and remove the background.
3.  Download the processed images once the background has been removed.
