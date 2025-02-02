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
        self.root.geometry("400x400")
        
        self.debug_box = tk.Text(self.root, height=10, width=50)
        self.debug_box.pack(pady=10)
        self.debug_box.insert(tk.END, "Debug Information:\n")
        
        self.text_box = tk.Text(self.root, height=10, width=50)
        self.text_box.pack(pady=10)
        
        self.start_button = tk.Button(self.root, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(self.root, text="Stop Listening", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.is_listening = False
        self.recording_thread = None
        self.audio_stream = None
        self.recognizer = sr.Recognizer()
        
        self.list_audio_devices()

    def log_debug(self, message):
        print(message)
        self.root.after(0, self._update_debug, message)

    def _update_debug(self, message):
        self.debug_box.insert(tk.END, f"{message}\n")
        self.debug_box.see(tk.END)

    def list_audio_devices(self):
        p = pyaudio.PyAudio()
        self.log_debug("\nAvailable Audio Devices:")
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        
        for i in range(numdevices):
            device_info = p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                self.log_debug(f"Input Device id {i} - {device_info.get('name')}")
        
        default_input = p.get_default_input_device_info()
        self.log_debug(f"\nDefault Input Device: {default_input['name']} (ID: {default_input['index']})")
        p.terminate()

    def start_listening(self):
        self.log_debug("\nStart Listening button pressed.")
        self.text_box.delete(1.0, tk.END)
        self.is_listening = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        if self.recording_thread is None or not self.recording_thread.is_alive():
            self.log_debug("Starting recording thread...")
            self.recording_thread = threading.Thread(target=self.listen_and_transcribe)
            self.recording_thread.daemon = True
            self.recording_thread.start()
        else:
            self.log_debug("Recording thread is already running.")

    def stop_listening(self):
        self.log_debug("\nStop Listening button pressed.")
        self.is_listening = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def listen_and_transcribe(self):
        """New method using speech_recognition directly with microphone"""
        self.log_debug("Initializing microphone...")
        
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.log_debug("Adjusting for ambient noise... Please wait...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.log_debug("Ambient noise adjustment complete.")
            
            while self.is_listening:
                try:
                    self.log_debug("Listening for speech...")
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5)
                    self.log_debug("Audio captured, transcribing...")
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        self.log_debug(f"Transcribed: {text}")
                        self.display_text(text)
                    except sr.UnknownValueError:
                        self.log_debug("Speech not recognized")
                    except sr.RequestError as e:
                        self.log_debug(f"Could not request results from service: {e}")
                        
                except Exception as e:
                    self.log_debug(f"Error during listening: {e}")
                    if not self.is_listening:
                        break
        
        self.log_debug("Stopped listening.")

    def display_text(self, text):
        self.root.after(0, self._update_text, text)

    def _update_text(self, text):
        self.text_box.insert(tk.END, f"{text}\n")
        self.text_box.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()