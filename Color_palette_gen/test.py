import argparse
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def rgb_to_hex(color):
    """
    Convert an RGB tuple to HEX color code.

    :param color: Tuple of RGB values
    :return: Hexadecimal string representation of the color
    """
    return "#{:02x}{:02x}{:02x}".format(*color)


def extract_3_colors(image_path):
    """
    Extract 3 prominent colors from the given image using KMeans clustering.

    :param image_path: Path to the input image
    :return: List of 3 RGB tuples representing the extracted colors
    """
    image = Image.open(image_path)
    image = image.resize((100, 100))  # Resize for faster processing
    image_data = np.array(image)

    pixels = image_data.reshape((-1, 3))  # Flatten the image pixels

    # Use KMeans to extract 3 dominant colors
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(pixels)
    dominant_colors = kmeans.cluster_centers_.astype(int)

    # Convert numpy.int64 to plain integers
    return [tuple(map(int, color)) for color in dominant_colors]


def display_palette_60_30_10(colors):
    """
    Display the 60-30-10 palette as a proportional bar plot with a side legend for RGB and HEX codes.

    :param colors: List of RGB tuples representing the colors
    """
    proportions = [0.6, 0.3, 0.1]  # 60%, 30%, and 10%
    fig, ax = plt.subplots(figsize=(8, 4))  # Wider for proportional bars and side legend
    start = 0  # Starting position for each color block

    # Draw proportional color blocks
    for i, (color, proportion) in enumerate(zip(colors, proportions)):
        # Add the color block
        ax.add_patch(plt.Rectangle((start, 0), proportion, 1, color=np.array(color) / 255))
        
        # Add percentage text at the center of each block
        text_x = start + proportion / 2  # Center horizontally
        text_y = 0.5  # Center vertically
        text_color = 'white' if sum(color) < 400 else 'black'  # Contrast for readability
        ax.text(text_x, text_y, f"{int(proportion * 100)}%", 
                ha='center', va='center', fontsize=12, color=text_color, fontweight='bold')
        
        start += proportion  # Update starting position for the next block

    # Adjust the limits and remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Add a side legend for colors with dots and labels
    for i, color in enumerate(colors):
        legend_x = 1.05  # X position of the legend
        legend_y = 0.8 - (i * 0.2)  # Position dots vertically
        hex_color = rgb_to_hex(color)

        # Draw color dot (circle)
        ax.add_patch(plt.Circle((legend_x, legend_y), 0.05, color=np.array(color) / 255, transform=ax.transAxes))
        
        # Add RGB and HEX text
        ax.text(legend_x + 0.08, legend_y, 
                f"RGB: {color}\nHEX: {hex_color}", 
                ha='left', va='center', fontsize=10, color='black', transform=ax.transAxes)

    plt.title("60-30-10 Color Palette", fontsize=14, pad=15)
    plt.tight_layout()
    plt.show()


def save_palette_60_30_10(colors, output_file='palette_60_30_10.txt'):
    """
    Save the 60-30-10 palette colors to a text file.

    :param colors: List of RGB tuples
    :param output_file: File to save the palette
    """
    proportions = [60, 30, 10]
    with open(output_file, 'w') as f:
        for color, percentage in zip(colors, proportions):
            f.write(f"{percentage}% - RGB: {color}, HEX: {rgb_to_hex(color)}\n")
    print(f"Palette saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="60-30-10 Color Palette Generator")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("-o", "--output", default="palette_60_30_10.txt", help="File to save the palette")
    args = parser.parse_args()

    # Extract colors
    colors = extract_3_colors(args.image_path)
    print("Extracted Colors (60-30-10):")
    print(f"60%: RGB {colors[0]}, HEX {rgb_to_hex(colors[0])}")
    print(f"30%: RGB {colors[1]}, HEX {rgb_to_hex(colors[1])}")
    print(f"10%: RGB {colors[2]}, HEX {rgb_to_hex(colors[2])}")

    # Display palette
    display_palette_60_30_10(colors)

    # Save palette
    save_palette_60_30_10(colors, args.output)


if __name__ == "__main__":
    main()
