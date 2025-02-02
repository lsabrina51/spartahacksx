import os
import time
import tkinter as tk
import pyaudio
import wave
import random
import uuid
from google.cloud import speech
from google.cloud import dialogflow_v2 as dialogflow
from google.cloud import texttospeech
from tkinter import messagebox
from threading import Thread, Lock
import queue

# Set Google API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "spartahack-449702-01bf43c0d13d.json"

class SpeechDialogSystem:
    def __init__(self):
        self.speech_client = speech.SpeechClient()
        self.session_id = str(uuid.uuid4())
        self.message_queue = queue.Queue()
        self.text_to_speech_client = texttospeech.TextToSpeechClient()
        self.is_running = True
        self.audio_lock = Lock()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Speech Dialog System")
        self.root.geometry("600x400")
        
        # Create text display
        self.text_display = tk.Text(self.root, height=20, width=60)
        self.text_display.pack(pady=10)
        
        # Create control buttons
        self.start_button = tk.Button(self.root, text="Start", command=self.start_system)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_system)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Initialize audio settings
        self.setup_audio()

    def setup_audio(self):
        self.p = pyaudio.PyAudio()
        # List available devices
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        
        self.log_message("Available Audio Devices:")
        for i in range(numdevices):
            device_info = self.p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                self.log_message(f"Input Device {i}: {device_info.get('name')}")

    def log_message(self, message):
        self.root.after(0, lambda: self.text_display.insert(tk.END, f"{message}\n"))
        self.root.after(0, lambda: self.text_display.see(tk.END))

    def record_audio(self):
        with self.audio_lock:
            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=1,  # Adjust based on your microphone
                frames_per_buffer=1024
            )
            
            self.log_message("Recording...")
            frames = []
            
            # Record for 5 seconds
            for _ in range(0, int(16000 / 1024 * 5)):
                if not self.is_running:
                    break
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            self.log_message("Recording finished.")
            return b''.join(frames)

    def recognize_speech(self, audio_data):
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        
        try:
            response = self.speech_client.recognize(config=config, audio=audio)
            if response.results:
                return response.results[0].alternatives[0].transcript
        except Exception as e:
            self.log_message(f"Speech recognition error: {e}")
        return ""

    def get_dialogflow_response(self, text, mood):
        if not text:
            return "No input received."
            
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path('spartahack-449702', self.session_id)
        
        # Modify prompt based on mood
        if mood == "evil":
            prompt = f"Act critical and lead people in the wrong direction. Respond in a mean, unhelpful way. The question is: {text}"
        else:
            prompt = f"Be kind, supportive, and give good advice. Respond in a positive, encouraging way. The question is: {text}"
        
        text_input = dialogflow.TextInput(text=prompt, language_code='en')
        query_input = dialogflow.QueryInput(text=text_input)
        
        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
            return response.query_result.fulfillment_text
        except Exception as e:
            self.log_message(f"Dialogflow error: {e}")
            return "Sorry, I couldn't process that."

    def text_to_speech(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Select voice based on mood
        if "Evil:" in text:
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-D",
                ssml_gender=texttospeech.SsmlVoiceGender.MALE
            )
        else:
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-C",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        
        try:
            response = self.text_to_speech_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Play audio
            with self.audio_lock:
                stream = self.p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    output=True
                )
                stream.write(response.audio_content)
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            self.log_message(f"Text-to-speech error: {e}")

    def process_audio(self):
        while self.is_running:
            # Record and recognize speech
            audio_data = self.record_audio()
            if not self.is_running:
                break
                
            transcription = self.recognize_speech(audio_data)
            if transcription:
                self.log_message(f"You said: {transcription}")
                
                # Get response from Dialogflow
                mood = random.choice(["evil", "good"])
                response = self.get_dialogflow_response(transcription, mood)
                final_response = f"{'Evil' if mood == 'evil' else 'Good'}: {response}"
                
                self.log_message(f"Response: {final_response}")
                
                # Convert response to speech
                self.text_to_speech(final_response)

    def start_system(self):
        self.is_running = True
        Thread(target=self.process_audio, daemon=True).start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_system(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()
        self.p.terminate()

if __name__ == "__main__":
    system = SpeechDialogSystem()
    system.run()