import os
from openai import OpenAI
import tempfile
import pygame
import time

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def create_and_play_test_audio():
    """Create and play a test audio file using OpenAI TTS and pygame"""
    try:
        print("Generating test audio...")
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input="This is a test of the text to speech system. If you can hear this, audio playback is working correctly."
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            print(f"Saving audio to: {temp_file.name}")
            response.stream_to_file(temp_file.name)
            
            # Initialize pygame mixer
            print("Initializing audio playback...")
            pygame.mixer.init()
            
            # Load and play the audio
            print("Playing audio...")
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            pygame.mixer.quit()
            os.unlink(temp_file.name)
            
    except Exception as e:
        print(f"Error: {e}")

def check_dependencies():
    try:
        import pygame
        print("Dependencies already installed")
    except ImportError:
        print("Please install required packages:")
        print("pip install pygame")
        return False
    return True

if __name__ == "__main__":
    if check_dependencies():
        create_and_play_test_audio()