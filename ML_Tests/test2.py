# Import necessary libraries
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist
import numpy as np

# Step 1: Load and Preprocess the Data (MNIST dataset)
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

# Normalize the image data to values between 0 and 1
train_images = train_images.astype('float32') / 255
test_images = test_images.astype('float32') / 255

# Reshape the data to fit the input requirements of the neural network
train_images = train_images.reshape((train_images.shape[0], 28, 28, 1))
test_images = test_images.reshape((test_images.shape[0], 28, 28, 1))

# Step 2: Build the Neural Network Model
model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.Flatten())
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(10, activation='softmax'))

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(train_images, train_labels, epochs=5, batch_size=64, validation_split=0.2)

# Step 3: Save the Model
# Save the entire model to a file
model.save('mnist_trained_model.h5')  # Save the model as an HDF5 file
print("Model saved to mnist_trained_model.h5")

# Step 4: Load the Saved Model
# Load the model from the file
loaded_model = tf.keras.models.load_model('mnist_trained_model.h5')
print("Model loaded from mnist_trained_model.h5")

# Step 5: Make Predictions with the Loaded Model
# Get predictions for the test dataset
predictions = loaded_model.predict(test_images)

# Step 6: Display a few predictions
# Show the predicted label for the first 5 images in the test set
for i in range(5):
    predicted_label = np.argmax(predictions[i])
    actual_label = test_labels[i]
    print(f"Image {i+1}: Predicted Label = {predicted_label}, Actual Label = {actual_label}")
