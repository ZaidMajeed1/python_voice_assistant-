import io
import os
import subprocess
import sys
import tempfile
import time
import wave
import webbrowser

import numpy as np
import sounddevice as sd
import speech_recognition as sr
from google import genai
from gtts import gTTS
from just_playback import Playback

# ---------------------------------------------------------
# 1. Initialize Gemini API Client
# ---------------------------------------------------------
api_key = "AIzaSyYourActualKeyHere"  # <-- Paste your API key here

if not api_key:
    print("Error: API key is missing.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# 2. Fast Audio Playback
# ---------------------------------------------------------
def speak(text):
    """Converts text to speech and plays it immediately."""
    print(f"\n🤖 Assistant: {text}")
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_filename = fp.name
            
        tts.save(temp_filename)
        
        player = Playback()
        player.load_file(temp_filename)
        player.play()
        
        while player.active:
            time.sleep(0.05)
            
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
    except Exception as e:
        print(f"⚠️ TTS/Playback Error: {e}")

# ---------------------------------------------------------
# 3. Optimized Fast Recording (4 Seconds max)
# ---------------------------------------------------------
def record_audio(duration=4, samplerate=16000):
    print(f"\n🎤 Listening... (Speak now)")
    
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("⚡ Processing...")
    
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    
    wav_io.seek(0)
    return wav_io

def listen():
    recognizer = sr.Recognizer()
    try:
        audio_stream = record_audio(duration=4)
        with sr.AudioFile(audio_stream) as source:
            audio = recognizer.record(source)
            
        text = recognizer.recognize_google(audio)
        print(f"👤 You: {text}")
        return text
    except sr.UnknownValueError:
        print("❓ Didn't catch that.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Speech service error: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Audio error: {e}")
        return None

# ---------------------------------------------------------
# 4. Laptop Control & Pro Search Commands
# ---------------------------------------------------------
def handle_laptop_commands(text, user_name):
    """Executes system shortcuts, opens apps, or performs pro web searches."""
    text_lower = text.lower()
    
    # App Launching Shortcuts
    if "open notepad" in text_lower:
        speak(f"Opening Notepad for you, {user_name}.")
        subprocess.Popen(["notepad.exe"])
        return True
    elif "open calculator" in text_lower:
        speak(f"Opening Calculator, {user_name}.")
        subprocess.Popen(["calc.exe"])
        return True
    elif "open chrome" in text_lower or "open browser" in text_lower:
        speak(f"Opening Chrome browser, {user_name}.")
        os.system("start chrome")
        return True
    elif "open code" in text_lower or "open vs code" in text_lower:
        speak(f"Launching Visual Studio Code, {user_name}.")
        os.system("code")
        return True
        
    # Pro Web / YouTube Searching Shortcuts
    elif "search for" in text_lower or "google" in text_lower:
        query = text_lower.replace("search for", "").replace("google", "").strip()
        speak(f"Searching Google for {query}, {user_name}.")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True
    elif "youtube" in text_lower:
        query = text_lower.replace("search on youtube", "").replace("youtube", "").strip()
        speak(f"Opening YouTube for {query}, {user_name}.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return True
        
    return False

# ---------------------------------------------------------
# 5. Ultra-Fast Gemini Generation with Fallback
# ---------------------------------------------------------
def get_ai_response(prompt, user_name):
    """Fetches a lightning-fast response with automatic model fallback on 503 errors."""
    models_to_try = ['gemini-3.6-flash', 'gemini-3.5-flash-lite']
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    'system_instruction': f'You are a lightning-fast personal voice assistant for {user_name}. Address him or her by name if appropriate. Answer in 1 short sentence maximum.',
                    'max_output_tokens': 50
                }
            )
            return response.text.strip()
        except Exception as e:
            continue
            
    return f"I'm experiencing heavy traffic right now, {user_name}. Let's try again in a moment."

# ---------------------------------------------------------
# 6. Main Assistant Loop
# ---------------------------------------------------------
def main():
    speak("Voice assistant online. What is your name?")
    
    # Listen for the user's name
    name_input = listen()
    if name_input:
        # Clean up speech like "my name is Zaid" -> "Zaid"
        user_name = name_input.replace("my name is", "").replace("i am", "").strip().title()
    else:
        user_name = "Friend"
        
    speak(f"Hello {user_name}. How can I help you today?")
    
    while True:
        user_input = listen()
        
        if not user_input:
            continue
            
        if any(word in user_input.lower() for word in ["exit", "quit", "stop", "bye"]):
            speak(f"Goodbye, {user_name}! Have a great day.")
            break
            
        # Check if the user wants to open apps or search the web
        if handle_laptop_commands(user_input, user_name):
            continue
            
        # Otherwise, let Gemini answer the query dynamically using their name
        reply = get_ai_response(user_input, user_name)
        speak(reply)

if __name__ == "__main__":
    main()