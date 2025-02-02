import tkinter as tk
from tkinter import filedialog, Toplevel
from PIL import Image, ImageTk, ImageEnhance, ImageOps

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

        # Deploy Button (to show the processed images)
        self.deploy_button = tk.Button(self.frame, text="Deploy", state=tk.DISABLED, command=self.deploy_program)
        self.deploy_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Image variables
        self.original_image = None
        self.good_image = None
        self.evil_image = None

    def deploy_program(self): 
        if self.good_image and self.evil_image:
            self.show_good_persona()
            self.show_evil_persona()
            self.hide_upload_interface()  # Hide the upload interface

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png"), ("Image Files", "*.jpg"), ("Image Files", "*.jpeg")])
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

            # Enable the deploy button
            self.deploy_button.config(state=tk.NORMAL)

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

    def display_image(self, img, canvas):
        img_resized = img.resize((256, 256))
        img_tk = ImageTk.PhotoImage(img_resized)
        canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
        canvas.image = img_tk  # Keep a reference to the image

    def show_good_persona(self):
        top = Toplevel(self.root)
        top.title("Good Persona")
        
        img_resized = self.good_image.resize((512, 512))
        img_tk = ImageTk.PhotoImage(img_resized)
        label = tk.Label(top, image=img_tk)
        label.image = img_tk  # Keep a reference to the image
        label.pack()

        # Textbox for additional input or information
        self.good_textbox = tk.Text(top, height=5, width=50)  # Adjust height and width as needed
        self.good_textbox.pack(pady=10)  # Add some padding for spacing

    def show_evil_persona(self):
        top = Toplevel(self.root)
        top.title("Evil Persona")
        
        img_resized = self.evil_image.resize((512, 512))
        img_tk = ImageTk.PhotoImage(img_resized)
        label = tk.Label(top, image=img_tk)
        label.image = img_tk  # Keep a reference to the image
        label.pack()

        # Textbox for additional input or information
        self.evil_textbox = tk.Text(top, height=5, width=50)  # Adjust height and width as needed
        self.evil_textbox.pack(pady=10)  # Add some padding for spacing

    def hide_upload_interface(self):
        # Hide the upload button and related labels and canvases
        self.upload_button.grid_forget()
        self.good_label.grid_forget()
        self.good_canvas.grid_forget()
        self.evil_label.grid_forget()
        self.evil_canvas.grid_forget()
        self.title.grid_forget()  # Hide the title
        self.frame.grid_forget()  # Hide the entire frame

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonaPhotoBooth(root)
    root.mainloop()