import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageOps
import os

class PersonaPhotoBooth:
    def __init__(self, root):
        self.root = root
        self.root.title("Persona Photo Booth")
        
        # Create a frame to hold the widgets
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        # Title
        self.title = tk.Label(self.frame, text="Persona Photo Booth", font=("Arial", 24))
        self.title.grid(row=0, column=0, columnspan=2, pady=20)

        # Image Upload Button
        self.upload_button = tk.Button(self.frame, text="Upload Image", command=self.upload_image)
        self.upload_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Canvas for displaying the images
        self.good_label = tk.Label(self.frame, text="Good Persona")
        self.good_label.grid(row=2, column=0)
        self.good_canvas = tk.Canvas(self.frame, width=256, height=256, bg="white")
        self.good_canvas.grid(row=3, column=0)

        self.evil_label = tk.Label(self.frame, text="Evil Persona")
        self.evil_label.grid(row=2, column=1)
        self.evil_canvas = tk.Canvas(self.frame, width=256, height=256, bg="white")
        self.evil_canvas.grid(row=3, column=1)

        # Download Buttons
        self.download_good_button = tk.Button(self.frame, text="Download Good Persona", state=tk.DISABLED, command=self.download_good_persona)
        self.download_good_button.grid(row=4, column=0, pady=10)

        self.download_evil_button = tk.Button(self.frame, text="Download Evil Persona", state=tk.DISABLED, command=self.download_evil_persona)
        self.download_evil_button.grid(row=4, column=1, pady=10)

        # Image variables
        self.original_image = None
        self.good_image = None
        self.evil_image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.process_image()

    def process_image(self):
        if self.original_image:
            # Create a copy for the good persona and evil persona
            self.good_image = self.original_image.copy()
            self.evil_image = self.original_image.copy()

            # Apply the "Good Persona" filter
            self.apply_good_persona(self.good_image)

            # Apply the "Evil Persona" filter
            self.apply_evil_persona(self.evil_image)

            # Display the processed images
            self.display_image(self.good_image, self.good_canvas)
            self.display_image(self.evil_image, self.evil_canvas)

            # Enable the download buttons
            self.download_good_button.config(state=tk.NORMAL)
            self.download_evil_button.config(state=tk.NORMAL)

    def apply_good_persona(self, img):
        # Apply brightness enhancement (brighten the image)
        enhancer = ImageEnhance.Brightness(img)
        img.paste(enhancer.enhance(1.2))

    def apply_evil_persona(self, img):
        # Apply brightness reduction and grayscale
        enhancer = ImageEnhance.Brightness(img)
        img.paste(enhancer.enhance(0.8))
        img = ImageOps.grayscale(img)
        self.evil_image = img.convert("RGB")

    def display_image(self, img, canvas):
        img_resized = img.resize((256, 256))
        img_tk = ImageTk.PhotoImage(img_resized)
        canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
        canvas.image = img_tk  # Keep a reference to the image

    def download_good_persona(self):
        if self.good_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if file_path:
                self.good_image.save(file_path)

    def download_evil_persona(self):
        if self.evil_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if file_path:
                self.evil_image.save(file_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = PersonaPhotoBooth(root)
    root.mainloop()