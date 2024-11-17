import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.datasets import mnist
import tkinter as tk
from PIL import Image, ImageOps, ImageGrab

# Load and preprocess the MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0  # Normalize the data

# Build a simple neural network model
model = Sequential([
    Flatten(input_shape=(28, 28)),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(x_train, y_train, epochs=5)

# Evaluate the model
model.evaluate(x_test, y_test)

# Build the GUI with Tkinter for digit drawing
class DigitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digit Recognizer")

        self.canvas = tk.Canvas(self.root, width=200, height=200, bg="white")
        self.canvas.grid(row=0, column=0, pady=2, padx=2)
        self.canvas.bind("<B1-Motion>", self.paint)

        self.button_clear = tk.Button(self.root, text="Clear", command=self.clear_canvas)
        self.button_clear.grid(row=1, column=0, pady=2)

        self.button_predict = tk.Button(self.root, text="Predict", command=self.predict_digit)
        self.button_predict.grid(row=2, column=0, pady=2)

        self.label = tk.Label(self.root, text="Draw a digit", font=("Helvetica", 16))
        self.label.grid(row=3, column=0, pady=2)

        self.image = None

    def clear_canvas(self):
        self.canvas.delete("all")

    def paint(self, event):
        # Draw on canvas
        x1, y1 = (event.x - 10), (event.y - 10)
        x2, y2 = (event.x + 10), (event.y + 10)
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", width=5)

    def predict_digit(self):
        # Save canvas as image and resize to 28x28
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        # Capture the canvas area and convert to grayscale
        img = ImageGrab.grab().crop((x, y, x1, y1))
        img = img.resize((28, 28))
        img = ImageOps.grayscale(img)
        
        # Convert the image to a NumPy array and normalize it
        img = np.array(img)
        img = img / 255.0
        img = img.reshape(1, 28, 28)

        # Predict the digit
        prediction = model.predict(img)
        digit = np.argmax(prediction)

        # Update the label with the predicted digit
        self.label.config(text=f"Prediction: {digit}")

# Start the application
root = tk.Tk()
app = DigitApp(root)
root.mainloop()
