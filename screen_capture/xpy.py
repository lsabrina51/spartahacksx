import time
import os
import mss
from PIL import Image
import pytesseract
from collections import deque

# Directory to save screenshots
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# Queue to store the most recent screenshots
recent_screenshots = deque(maxlen=5)

# Function to capture a screenshot
def capture_screenshot():
    with mss.mss() as sct:
        # Capture the entire screen
        screenshot = sct.shot(output=os.path.join(screenshot_dir, "screenshot.png"))
        return screenshot

# Function to perform OCR on images
def perform_ocr_on_images(images):
    text_results = []
    for img in images:
        # Open the image and perform OCR
        image = Image.open(img)
        text = pytesseract.image_to_string(image)
        text_results.append(text)
    return text_results

def main():
    while True:
        # Capture a screenshot and add to the queue
        screenshot_path = capture_screenshot()
        recent_screenshots.append(screenshot_path)
        print(f"Captured screenshot: {screenshot_path}")

        # Wait for 3 seconds before the next screenshot
        time.sleep(3)

        # Every 15 seconds, perform OCR on the recent screenshots
        if len(recent_screenshots) >= 5:
            time.sleep(12)  # Wait for 12 seconds (total 15 seconds from first capture)
            print("Performing OCR on the most recent 5 screenshots...")
            text_results = perform_ocr_on_images(recent_screenshots)

            # Print OCR results
            for i, text in enumerate(text_results, start=1):
                print(f"Text from screenshot {i}:")
                print(text)
                print("-" * 40)

if __name__ == "__main__":
    main()