import os
import pyaudio
from google.cloud import texttospeech

# Function to generate and stream speech from text using Google Cloud Text-to-Speech API
def generate_and_play_speech(text, voice_type="good"):
    # Set up Google Cloud client
    client = texttospeech.TextToSpeechClient()

    # Select voice parameters based on the type
    if voice_type == "good":
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D",  # Friendly, cheerful voice
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
    elif voice_type == "evil":
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-A",  # Darker, more sinister voice
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
    else:
        print("Invalid voice type. Choose either 'good' or 'evil'.")
        return

    # Set audio configuration
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=1.0,  # Adjust speaking speed if needed
    )

    # Synthesize speech
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice_params, audio_config=audio_config
    )

    # Stream the audio in real-time using pyaudio
    stream_audio(response.audio_content)

# Function to stream audio in real-time using pyaudio
def stream_audio(audio_content):
    # Set up pyaudio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True)

    # Write the audio content to the stream in chunks
    chunk_size = 1024
    for i in range(0, len(audio_content), chunk_size):
        stream.write(audio_content[i:i+chunk_size])

    # Close the stream after playing the audio
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Audio playback finished. Program will now close.")

# Function to process the input file
def process_input_file(input_file):
    with open(input_file, "r") as file:
        lines = file.readlines()

    if not lines:
        print("Input file is empty!")
        return

    # Extract the first word (which determines the voice type)
    first_word = lines[0].split()[0].lower()  # Take the first word and convert to lowercase
    text = "".join(lines)  # Join all lines to form the full text

    if first_word == "good":
        generate_and_play_speech(text, voice_type="good")
    elif first_word == "evil":
        generate_and_play_speech(text, voice_type="evil")
    else:
        print("The first word must be either 'good' or 'evil' to specify the speech type.")

if __name__ == "__main__":
    input_file = "input.txt"  # Replace with your input file path
    process_input_file(input_file)
