import time
import threading
import mss
import pytesseract
from PIL import Image
from collections import deque
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Queue to store recent screenshots
screenshot_queue = deque(maxlen=5)

def capture_screenshot():
    with mss.mss() as sct:
        screenshot_path = "screenshot.png"  # Temporary file
        sct.shot(output=screenshot_path)
        img = Image.open(screenshot_path)
        screenshot_queue.append(img)


def ocr_latest_screenshots():
    if not screenshot_queue:
        update_text("No screenshots available for OCR.\n")
        return
    
    update_text("Performing OCR on the latest 5 screenshots:\n")
    for i, img in enumerate(screenshot_queue):
        text = pytesseract.image_to_string(img)
        update_text(f"Screenshot {i+1} OCR Result:\n{text}\n")

def update_text(text):
    text_widget.insert(tk.END, text + "\n")
    text_widget.yview(tk.END)

def screenshot_loop():
    while True:
        capture_screenshot()
        time.sleep(3)

def ocr_loop():
    while True:
        time.sleep(15)
        ocr_latest_screenshots()

# Initialize Tkinter window
root = tk.Tk()
root.title("OCR Screenshot Viewer")
text_widget = ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_widget.pack(padx=10, pady=10)

# Start screenshot and OCR threads
screenshot_thread = threading.Thread(target=screenshot_loop, daemon=True)
ocr_thread = threading.Thread(target=ocr_loop, daemon=True)

screenshot_thread.start()
ocr_thread.start()

# Run the Tkinter main loop
root.mainloop()
