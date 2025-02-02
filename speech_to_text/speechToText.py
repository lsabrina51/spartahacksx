import os
import pyaudio
import wave
import speech_recognition as sr
import tkinter as tk
from tkinter import messagebox
import time
import threading

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text")
        self.root.geometry("400x200")
        
        self.text_box = tk.Text(self.root, height=10, width=50)
        self.text_box.pack(pady=20)
        
        self.start_button = tk.Button(self.root, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=10)
        
        self.stop_button = tk.Button(self.root, text="Stop Listening", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(pady=10)
        
        self.is_listening = False
        self.recording_thread = None
        self.audio_stream = None
        self.recognizer = sr.Recognizer()

    def start_listening(self):
        print("Start Listening button pressed.")
        self.text_box.delete(1.0, tk.END)  # Clear the text box before starting
        self.is_listening = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start the background thread for capturing and processing audio
        if self.recording_thread is None or not self.recording_thread.is_alive():
            print("Starting recording thread...")
            self.recording_thread = threading.Thread(target=self.capture_audio)
            self.recording_thread.daemon = True  # Ensure the thread closes when the main program exits
            self.recording_thread.start()
        else:
            print("Recording thread is already running.")

    def stop_listening(self):
        print("Stop Listening button pressed.")
        self.is_listening = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Wait for the recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()
    
    def capture_audio(self):
        print("Capture Audio thread started.")
        # Set up audio stream
        p = pyaudio.PyAudio()
        chunk_size = 1024  # Size of audio chunks (1 second of audio)
        sample_format = pyaudio.paInt16
        channels = 1
        rate = 44100  # Sample rate
        frames_per_buffer = int(rate * 15)  # Capture 15 seconds of audio

        try:
            self.audio_stream = p.open(format=sample_format, channels=channels, rate=rate,
                                       input=True, frames_per_buffer=chunk_size)
            print("Audio stream initialized.")
        except Exception as e:
            print(f"Error initializing audio stream: {e}")
            return

        audio_frames = []

        while self.is_listening:
            # Capture audio in chunks
            try:
                audio_data = self.audio_stream.read(chunk_size)
                audio_frames.append(audio_data)
                print("Captured audio chunk.")
            except Exception as e:
                print(f"Error capturing audio chunk: {e}")
                break

            if len(audio_frames) >= frames_per_buffer:
                print("15 seconds of audio captured, saving and processing...")
                # Save the 15-second chunk to a .wav file
                self.save_audio(audio_frames)
                audio_frames = []  # Reset frames after saving

                # Process the audio to text
                self.process_audio(audio_frames)

        # Close the audio stream after stopping
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            print("Audio stream closed.")

    def save_audio(self, audio_frames):
        filename = f"audio_{int(time.time())}.wav"
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_frames))
        print(f"Saved audio file: {filename}")

    def process_audio(self, audio_frames):
        print("Processing audio...")
        # Convert the audio to a format suitable for SpeechRecognition
        audio_data = b''.join(audio_frames)  # Convert frames to a single byte string
        audio_file_path = "temp.wav"

        # Save the audio to a temporary file
        with wave.open(audio_file_path, 'wb') as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(44100)
            audio_file.writeframes(audio_data)
        print(f"Audio saved to temporary file: {audio_file_path}")

        # Use SpeechRecognition to recognize the text from the audio file
        try:
            with sr.AudioFile(audio_file_path) as source:
                print("Recognizing speech...")
                audio = self.recognizer.record(source)  # Capture the entire audio
                text = self.recognizer.recognize_google(audio)  # Recognize speech
                print(f"Recognized text: {text}")
                self.display_text(text)
        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError as e:
            print(f"Error with the recognition service; {e}")

        # Clean up the temporary audio file
        self.cleanup_temp_file(audio_file_path)

    def cleanup_temp_file(self, file_path):
        try:
            if os.path.exists(file_path):  # Ensure the file exists before trying to remove it
                os.remove(file_path)
                print(f"Deleted temporary file: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error removing temp file: {e}")

    def display_text(self, text):
        # Safely update the Tkinter text box from the main thread
        print(f"Displaying recognized text: {text}")
        self.root.after(0, self._update_text, text)

    def _update_text(self, text):
        # This function is called from the main thread via after()
        self.text_box.insert(tk.END, f"{text}\n")
        self.text_box.yview(tk.END)  # Scroll to the bottom

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()
