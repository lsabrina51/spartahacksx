import os
import time
import pyaudio
from google.cloud import speech
from google.cloud import texttospeech
import random
from threading import Thread
from openai import OpenAI
#Sabrina code 
from sabrina_test import PersonaPhotoBooth
import tkinter as tk

root = tk.Tk()
app = PersonaPhotoBooth(root)


#end of sabrina code 

# Set Google API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "spartahack-449702-0585f5bb9a36.json"

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Google Speech-to-Text client
speech_client = speech.SpeechClient()

# Initialize Google Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

# Set directory to save MP3 files
output_dir = "audio_files"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Initialize counter for lexicographic naming of MP3 files
file_counter = 1

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
            f"The question is: {text}."
        )
    else:
        user_prompt = (
            "Respond in a kind, supportive, and encouraging way. "
            f"The question is: {text}."
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

# Function to save GPT response as MP3 file using Google Cloud Text-to-Speech
def save_audio_as_mp3(text, file_index):
    # Set up the text-to-speech request
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    # Synthesize speech
    response = tts_client.synthesize_speech(
        input=synthesis_input, 
        voice=voice, 
        audio_config=audio_config
    )
    
    # Create a file name in lexicographic order (e.g., 001.mp3, 002.mp3, etc.)
    file_name = f"{str(file_index).zfill(3)}.mp3"
    file_path = os.path.join(output_dir, file_name)

    # Write the audio content to the MP3 file
    with open(file_path, "wb") as out:
        out.write(response.audio_content)
    
    print(f"Saved {file_name}")

# Function to handle speech-to-text and GPT response pipeline
def process_speech_to_gpt():
    global file_counter  # Use the global file_counter to name MP3s in lexicographic order
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
            
            # Step 6: Save the GPT response as an MP3 file
            save_audio_as_mp3(gpt_response, file_counter)

            #sabrina code
            app.insert_into_textbox(mood, gpt_response)

            if mood == 'good' or mood is 'good': 
                app.show_good_persona(); 
                app.insert_into_textbox('good', gpt_response)
            if mood == 'bad' or mood is 'bad':
                app.show_bad_persona(); 
                app.insert_into_textbox('bad', gpt_response)
            

            

           #end sabrina


            # Increment the file counter for the next MP3 file
            file_counter += 1
        
        # Wait before starting the next cycle
        time.sleep(0.5)

# Start the process in a separate thread so it runs continuously
thread = Thread(target=process_speech_to_gpt)
thread.daemon = True
thread.start()

#sabrina code 
root.mainloop()
# Keep the main thread alive
try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    print("Exiting program.")
