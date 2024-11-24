import pyttsx3
import os
from datetime import datetime

# Directory and file setup
AUDIO_DIR = "output_audio"
TEXT_FILE = "output.txt"

# Ensure the audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

def text_to_speech(text, output_file):
    """
    Converts input text to speech and saves it as a .wav file.

    :param text: The text to convert to speech.
    :param output_file: The path of the output .wav file.
    """
    # Initialize the pyttsx3 TTS engine
    engine = pyttsx3.init()
    
    # Set properties for the speech
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

    # Create the .wav file
    engine.save_to_file(text, output_file)
    engine.runAndWait()

    print(f"Generated TTS file: {output_file}")

def append_text_to_file(text, file_name):
    """
    Appends the provided text to the specified text file.

    :param text: The text to append.
    :param file_name: The file to which the text will be appended.
    """
    with open(file_name, "a") as f:
        f.write(text + "\n")
    print(f"Text appended to {file_name}")

if __name__ == "__main__":
    # Take input from the terminal
    text = input("Enter the text to convert to speech: ").strip()

    if not text:
        print("No text provided. Exiting.")
    else:
        # Print the text in the terminal
        print(f"You entered: {text}")

        # Append the text to output.txt
        append_text_to_file(text, TEXT_FILE)

        # Generate unique audio file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file_name = f"audio_{timestamp}.wav"
        output_path = os.path.join(AUDIO_DIR, audio_file_name)

        # Convert text to speech and save it
        text_to_speech(text, output_path)
