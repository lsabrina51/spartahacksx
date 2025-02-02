import os
import time
import tkinter as tk
import pyaudio
import wave
from google.cloud import speech
from tkinter import messagebox
from threading import Thread

# Set Google API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "spartahack-449702-01bf43c0d13d.json"

# Initialize Google Speech-to-Text client
client = speech.SpeechClient()

# Set up microphone input
def record_audio():
    # Set up the microphone
    p = pyaudio.PyAudio()

    # List all available audio devices
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            print(f"Input Device {i}: {device_info.get('name')}")

    # You can manually set the input device index (change 1 to your device's index)
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, input_device_index=1, frames_per_buffer=1024)

    print("Recording...")

    frames = []
    for _ in range(0, int(16000 / 1024 * 15)):  # Record for 15 seconds
        data = stream.read(1024)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Recording finished.")
    return b''.join(frames)

# Google Speech-to-Text function
def recognize_speech(audio_data):
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript if response.results else ""

# Function to show popup (non-blocking in main thread)
def show_popup(transcription):
    def popup_thread():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Schedule the popup to be shown in the main thread
        root.after(0, lambda: messagebox.showinfo("Speech-to-Text Result", transcription))
        
        root.mainloop()  # Start Tkinter event loop

    # Start the popup in a separate thread
    thread = Thread(target=popup_thread)
    thread.daemon = True
    thread.start()

# Function to run the speech-to-text loop
def speech_to_text_loop():
    while True:
        # Step 1: Record audio from microphone for 15 seconds
        audio_data = record_audio()

        # Step 2: Recognize speech using Google API
        transcription = recognize_speech(audio_data)

        # Step 3: Show result in Tkinter popup (non-blocking)
        if transcription:
            show_popup(transcription)

        # Immediately restart recording without waiting for another 15 seconds
        time.sleep(0.5)  # Small delay before starting the next recording

# Start the loop in a separate thread so it runs continuously
thread = Thread(target=speech_to_text_loop)
thread.daemon = True
thread.start()

# Keep the main thread alive (this will keep the Tkinter pop-up from closing)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting program.")
