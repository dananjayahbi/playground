import cv2
import numpy as np
from tkinter import Tk, Label, Scale, HORIZONTAL, Button, filedialog, Frame
from PIL import Image, ImageTk


class AdvancedSpecsSimulatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Specs Simulator")

        # Main layout frames
        self.controls_frame = Frame(master)
        self.controls_frame.grid(row=0, column=0, sticky="nw")
        self.image_frame = Frame(master)
        self.image_frame.grid(row=0, column=1, sticky="nsew")

        # Initial variables
        self.image_path = None
        self.image = None
        self.image_rgb = None
        self.processed_image = None
        self.spherical_power = 0.0
        self.cylindrical_power = 0.0
        self.axis = 180

        # Load image button
        self.load_image_button = Button(self.controls_frame, text="Load Image", command=self.load_image)
        self.load_image_button.pack(pady=5)

        # Spherical power slider
        self.spherical_label = Label(self.controls_frame, text="Spherical Power (Plano):")
        self.spherical_label.pack(pady=5)
        self.spherical_slider = Scale(
            self.controls_frame, from_=-10.0, to=10.0, resolution=0.25, orient=HORIZONTAL, command=self.update_spherical
        )
        self.spherical_slider.set(self.spherical_power)
        self.spherical_slider.pack(pady=5)

        # Cylindrical power slider
        self.cylindrical_label = Label(self.controls_frame, text="Cylindrical Power:")
        self.cylindrical_label.pack(pady=5)
        self.cylindrical_slider = Scale(
            self.controls_frame, from_=-6.0, to=6.0, resolution=0.25, orient=HORIZONTAL, command=self.update_cylindrical
        )
        self.cylindrical_slider.set(self.cylindrical_power)
        self.cylindrical_slider.pack(pady=5)

        # Axis slider
        self.axis_label = Label(self.controls_frame, text="Axis (°):")
        self.axis_label.pack(pady=5)
        self.axis_slider = Scale(
            self.controls_frame, from_=0, to=180, resolution=1, orient=HORIZONTAL, command=self.update_axis
        )
        self.axis_slider.set(self.axis)
        self.axis_slider.pack(pady=5)

        # Display frame for image
        self.display_frame = Label(self.image_frame)
        self.display_frame.pack()

    def load_image(self):
        """
        Open a file dialog to load an image and update the display.
        """
        file_path = filedialog.askopenfilename(
            title="Select an image", filetypes=[("Image files", "*.jpg *.png *.jpeg")]
        )
        if file_path:
            self.image_path = file_path
            self.image = cv2.imread(self.image_path)
            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.processed_image = self.image_rgb  # Reset to original image
            self.apply_vision_correction()
            self.update_display()

    def apply_vision_correction(self):
        """
        Apply an advanced correction simulation based on spherical and cylindrical power, and axis.
        """
        if self.image_rgb is not None:
            height, width, _ = self.image_rgb.shape
            x = np.linspace(-1, 1, width)
            y = np.linspace(-1, 1, height)
            xv, yv = np.meshgrid(x, y)

            # Create a wavefront distortion map
            spherical_distortion = self.spherical_power * (xv**2 + yv**2)
            cylindrical_distortion = self.cylindrical_power * (xv * np.cos(np.deg2rad(self.axis)) + yv * np.sin(np.deg2rad(self.axis))) ** 2

            # Combine distortions
            wavefront = spherical_distortion + cylindrical_distortion

            # Normalize and apply distortion
            wavefront = cv2.normalize(wavefront, None, 0, 1, cv2.NORM_MINMAX)
            distorted_image = np.zeros_like(self.image_rgb, dtype=np.uint8)

            for channel in range(3):  # Apply distortion to each color channel
                distorted_image[:, :, channel] = cv2.remap(
                    self.image_rgb[:, :, channel],
                    (xv + wavefront * width).astype(np.float32),
                    (yv + wavefront * height).astype(np.float32),
                    interpolation=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REFLECT
                )

            self.processed_image = distorted_image

    def update_spherical(self, value):
        """
        Update the spherical power and reprocess the image.
        """
        self.spherical_power = float(value)
        self.apply_vision_correction()
        self.update_display()

    def update_cylindrical(self, value):
        """
        Update the cylindrical power and reprocess the image.
        """
        self.cylindrical_power = float(value)
        self.apply_vision_correction()
        self.update_display()

    def update_axis(self, value):
        """
        Update the axis and reprocess the image.
        """
        self.axis = int(value)
        self.apply_vision_correction()
        self.update_display()

    def update_display(self):
        """
        Update the displayed image in the GUI.
        """
        if self.processed_image is not None:
            # Resize the image for display if it's too large
            max_width, max_height = 1800, 1200
            image_height, image_width, _ = self.processed_image.shape

            scale = min(max_width / image_width, max_height / image_height, 1.0)
            resized_image = cv2.resize(
                self.processed_image,
                (int(image_width * scale), int(image_height * scale)),
                interpolation=cv2.INTER_AREA,
            )

            # Convert to a format usable by Tkinter
            img = Image.fromarray(resized_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.display_frame.imgtk = imgtk
            self.display_frame.configure(image=imgtk)


# Run the application
if __name__ == "__main__":
    root = Tk()
    app = AdvancedSpecsSimulatorApp(root)
    root.mainloop()
