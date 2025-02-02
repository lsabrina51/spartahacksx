import os
import time
import pyaudio
from google.cloud import speech
import random
from threading import Thread
from openai import OpenAI

# Set Google API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "spartahack-449702-01bf43c0d13d.json"

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Google Speech-to-Text client
speech_client = speech.SpeechClient()

# Record audio from the microphone
def record_audio():
    p = pyaudio.PyAudio()

    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            print(f"Input Device {i}: {device_info.get('name')}")

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

    response = speech_client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript if response.results else ""

# Function to determine whether the response should be 'good' or 'evil'
def determine_mood(input_text):
    if 'good' in input_text.lower():
        return 'good'
    elif 'evil' in input_text.lower():
        return 'evil'
    else:
        return random.choice(['good', 'evil'])

# Function to get GPT-3.5 response
def get_gpt3_response(mood, text):
    system_message = "You are an assistant that can respond in different moods."
    
    if mood == 'evil':
        user_prompt = (
            "Respond in a mean, unhelpful way (while keeping it appropriate and not harmful). "
            f"The question is: {text}"
        )
    else:
        user_prompt = (
            "Respond in a kind, supportive, and encouraging way. "
            f"The question is: {text}"
        )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {e}"

# Function to handle speech-to-text and GPT response pipeline
def process_speech_to_gpt():
    while True:
        # Step 1: Record audio for 15 seconds
        audio_data = record_audio()

        # Step 2: Recognize speech and get transcription
        transcription = recognize_speech(audio_data)
        if transcription:
            print(f"Transcription: {transcription}")

            # Step 3: Determine mood based on transcription
            mood = determine_mood(transcription)

            # Step 4: Get response from GPT-3.5
            gpt_response = get_gpt3_response(mood, transcription)

            # Step 5: Print or display the response
            print(f"[{mood.upper()}] GPT Response: {gpt_response}")
        
        # Wait before starting the next cycle
        time.sleep(0.5)

# Start the process in a separate thread so it runs continuously
thread = Thread(target=process_speech_to_gpt)
thread.daemon = True
thread.start()

# Keep the main thread alive
try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    print("Exiting program.")
