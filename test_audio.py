import io
import sys
import wave

from google import genai
import pyttsx3
import sounddevice as sd
import speech_recognition as sr

# ---------------------------------------------------------
# Initialize Text-to-Speech Engine
# ---------------------------------------------------------
engine = pyttsx3.init()

def speak(text):
    """Converts text to speech."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# ---------------------------------------------------------
# Test Recording using SoundDevice (No PyAudio needed)
# ---------------------------------------------------------
def test_listen(duration=5, samplerate=16000):
    print(f"\nRecording for {duration} seconds... Speak now!")

    # Record audio data as a NumPy array
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording finishes
    print("Processing recorded audio...")
    
    # Convert numpy array into an in-memory WAV file stream
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    
    wav_io.seek(0)
    
    # Pass the stream to SpeechRecognition
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_io) as source:
            audio = recognizer.record(source)
        
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio (did you speak?).")
        return None
    except sr.RequestError as e:
        print(f"Speech service error: {e}")
        return None
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    speak("Hello! Microphone test starting now.")
    user_input = test_listen(duration=5)
    
    if user_input:
        speak(f"Success! I heard you say: {user_input}")
    else:
        speak("Test failed. I couldn't pick up any speech. Check your microphone settings.")

# ---------------------------------------------------------
# 1. Initialize Gemini API Client
# ---------------------------------------------------------
api_key = "AQ.Ab8RN6KbVdQ_SOEbwlJnDOBOMgwiEvnaiIK_w-IZwfY7-x2D1g" # <-- Paste your key directly inside the quotes here

if not api_key:
    print("Error: GEMINI_API_KEY is missing.")
    sys.exit(1)

client = genai.Client(api_key=api_key)