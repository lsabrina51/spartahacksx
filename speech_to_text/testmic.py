import pyaudio

p = pyaudio.PyAudio()

# List all available audio input devices
print("Listing available devices:")
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

# Try to open a stream from the default microphone
try:
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)
    print("Successfully opened stream.")
    print("Recording for 5 seconds...")
    audio_data = stream.read(44100 * 5)  # Capture 5 seconds of audio
    print("Audio captured.")
    stream.stop_stream()
    stream.close()
except Exception as e:
    print(f"Error opening stream: {e}")
finally:
    p.terminate()
