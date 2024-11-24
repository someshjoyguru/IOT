import os
import time
import speech_recognition as sr
from datetime import datetime

# Initialize recognizer
recognizer = sr.Recognizer()

# Directory and file setup
AUDIO_DIR = "input_audio"
TEXT_FILE = "input.txt"

# Ensure the audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

def save_audio(audio, file_name):
    """Saves the audio to the input_audio folder."""
    file_path = os.path.join(AUDIO_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(audio.get_wav_data())
    print(f"Audio saved to {file_path}")
    return file_path

def append_text_to_file(text, file_name):
    """Appends the recognized text to the text file."""
    with open(file_name, "a") as f:
        f.write(text + "\n")
    print(f"Text appended to {file_name}")

def listen_and_process(duration=10):
    """
    Listens for speech and processes audio into text.
    Ends the process after the specified duration.
    """
    # Start timing
    start_time = time.time()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... please wait")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech...")

        try:
            # Listen for speech with a timeout equal to the remaining duration
            while time.time() - start_time < duration:
                print("Recording audio...")
                remaining_time = duration - (time.time() - start_time)
                if remaining_time <= 0:
                    break

                # Listen for speech
                audio = recognizer.listen(source, timeout=remaining_time, phrase_time_limit=remaining_time)
                print("Processing audio...")

                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio)
                print("You said:", text)

                # Generate a unique audio file name with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_file_name = f"audio_{timestamp}.wav"

                # Save audio and append text
                save_audio(audio, audio_file_name)
                append_text_to_file(text, TEXT_FILE)

        except sr.WaitTimeoutError:
            print("No speech detected within the given time. Exiting...")
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Starting speech-to-text process...")
    listen_and_process(duration=10)
    print("Listening process ended.")
