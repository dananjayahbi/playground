# Import necessary libraries
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt

# Step 1: Load the Saved Model
model = tf.keras.models.load_model('mnist_trained_model.h5')
print("Model loaded from mnist_trained_model.h5")

# Step 2: Load and Preprocess Your Custom Image
def preprocess_image(img_path):
    """Load and preprocess the image."""
    img = image.load_img(img_path, color_mode='grayscale', target_size=(28, 28))  # Load image as grayscale
    img = image.img_to_array(img)  # Convert image to array
    img = img.astype('float32') / 255  # Normalize the image (pixel values between 0 and 1)
    img = np.expand_dims(img, axis=0)  # Add batch dimension (1, 28, 28, 1)
    return img

# Provide the path to your custom image (e.g., 'my_digit.png')
img_path = 'testImg3.jpg'
custom_image = preprocess_image(img_path)

# Step 3: Make a Prediction with the Model
predictions = model.predict(custom_image)
predicted_label = np.argmax(predictions[0])

# Step 4: Display the Image and Prediction
plt.imshow(custom_image.squeeze(), cmap=plt.cm.binary)
plt.title(f"Predicted Label: {predicted_label}")
plt.show()

print(f"The model predicts this image is a: {predicted_label}")
