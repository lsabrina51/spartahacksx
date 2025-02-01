import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageOps
import os
import subprocess  # To run another program

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

        # Deploy Button (to execute another program)
        self.deploy_button = tk.Button(self.frame, text="Deploy", state=tk.DISABLED, command=self.deploy_program)
        self.deploy_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Image variables
        self.original_image = None
        self.good_image = None
        self.evil_image = None

    def upload_image(self):
        # Open the file dialog and allow multiple image file types
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png"), ("Image Files", "*.jpg"), ("Image Files", "*.jpeg")])
        
        # Debugging print statement to ensure the correct file path is selected
        print(f"Selected file path: {file_path}")
        
        if file_path:
            try:
                # Try opening the image
                self.original_image = Image.open(file_path)
                self.process_image()  # Process the image once loaded successfully
            except Exception as e:
                # If there's an error opening the file, show an error message
                print(f"Error opening image: {e}")
                # Optionally show a message box to inform the user
                tk.messagebox.showerror("File Error", "Unable to open the selected image file.")


    def process_image(self):
        if self.original_image:
            # Create a copy for the good persona and evil persona
            self.good_image = self.original_image.copy()
            self.evil_image = self.original_image.copy()

            # Apply the "Good Persona" filter
            self.apply_good_persona(self.good_image)

            # Apply the "Evil Persona" filter
            self.apply_evil_persona(self.evil_image)

            # Automatically download the images
            self.download_good_persona()
            self.download_evil_persona()

            # Enable the deploy button after downloading
            self.deploy_button.config(state=tk.NORMAL)

            # Close the window after downloading the images
            self.root.quit()

    def apply_good_persona(self, img):
        # Apply brightness enhancement (brighten the image)
        enhancer = ImageEnhance.Brightness(img)
        img.paste(enhancer.enhance(1.2))

    def apply_evil_persona(self, img):
        # Apply brightness reduction
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.8)
        
        # Convert to grayscale
        img = ImageOps.grayscale(img)
        
        # Add a red tint to the grayscale image
        red_overlay = Image.new("RGB", img.size, (255, 0, 0))  # Red color overlay
        img = Image.composite(img.convert("RGB"), red_overlay, img.convert("L"))  # Blend grayscale with red overlay
        
        # Final conversion to RGB
        self.evil_image = img

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

    def deploy_program(self):
        # Path to the other Python program you want to execute
        deploy_script_path = "deploy_script.py"  # Replace with your actual script path

        try:
            # Execute the other Python script
            subprocess.run(["python", deploy_script_path], check=True)
            print("Deployment successful!")
        except subprocess.CalledProcessError as e:
            print(f"Error during deployment: {e}")
        except FileNotFoundError:
            print(f"Deployment script not found: {deploy_script_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PersonaPhotoBooth(root)
    root.mainloop()
