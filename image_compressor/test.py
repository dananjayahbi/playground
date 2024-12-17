from PIL import Image
import os
import matplotlib.pyplot as plt

def compress_image(input_path, output_path, quality=85, format="JPEG"):
    """
    Compress an image, strip metadata, and reduce file size.

    Args:
        input_path (str): Path to the input image file.
        output_path (str): Path to save the compressed image.
        quality (int): Compression quality (1-100).
        format (str): Format to save the image (JPEG, WEBP).

    Returns:
        tuple: Original image size, compressed image size.
    """
    try:
        # Open the input image
        img = Image.open(input_path)
        
        # Strip metadata and convert mode
        img_no_exif = img.convert("RGB")

        # Save compressed image
        img_no_exif.save(output_path, format=format, optimize=True, quality=quality)

        # Get file sizes
        original_size = os.path.getsize(input_path) / 1024  # KB
        compressed_size = os.path.getsize(output_path) / 1024  # KB

        return original_size, compressed_size

    except Exception as e:
        print(f"Error: {e}")
        return None, None

def plot_images(input_path, output_path, original_size, compressed_size):
    """
    Plot the original and compressed images with file sizes.

    Args:
        input_path (str): Path to the original image.
        output_path (str): Path to the compressed image.
        original_size (float): Size of the original image (in KB).
        compressed_size (float): Size of the compressed image (in KB).
    """
    try:
        # Load images
        original_img = Image.open(input_path)
        compressed_img = Image.open(output_path)

        # Plot images side by side
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        axes[0].imshow(original_img)
        axes[0].axis("off")
        axes[0].set_title(f"Original Image\nSize: {original_size:.2f} KB")

        axes[1].imshow(compressed_img)
        axes[1].axis("off")
        axes[1].set_title(f"Compressed Image\nSize: {compressed_size:.2f} KB")

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error in plotting: {e}")

if __name__ == "__main__":
    # Paths for input and output
    input_image_path = "im1.jpg"   # Replace with your input file path
    output_image_path = "compressed_image.jpg"  # Output compressed file path

    # Compress the image
    original_size, compressed_size = compress_image(input_image_path, output_image_path, quality=20, format="JPEG")

    if original_size and compressed_size:
        # Plot comparison
        plot_images(input_image_path, output_image_path, original_size, compressed_size)
