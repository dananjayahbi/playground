# Import necessary libraries
import tensorflow as tf
import numpy as np
from tensorflow.keras.datasets import mnist
import matplotlib.pyplot as plt

# Step 1: Load the Saved Model
model = tf.keras.models.load_model('./mnist_trained_model.h5')
print("Model loaded from mnist_trained_model.h5")

# Step 2: Load and Preprocess the Data (MNIST test set)
(_, _), (test_images, test_labels) = mnist.load_data()

# Normalize the test image data to values between 0 and 1
test_images = test_images.astype('float32') / 255

# Reshape the data to fit the input requirements of the neural network
test_images = test_images.reshape((test_images.shape[0], 28, 28, 1))

# Step 3: Get Predictions from the Model
predictions = model.predict(test_images)

# Step 4: Display a Few Predictions and Compare with Actual Labels
def show_prediction(index):
    """Function to display image, predicted label, and actual label."""
    predicted_label = np.argmax(predictions[index])
    actual_label = test_labels[index]
    
    plt.imshow(test_images[index].reshape(28, 28), cmap=plt.cm.binary)
    plt.title(f"Predicted: {predicted_label}, Actual: {actual_label}")
    plt.show()

# Show predictions for the first 5 test images
for i in range(5):
    show_prediction(i)
