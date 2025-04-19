import requests
import openai
import os
import speech_recognition as sr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTY_IP = "192.168.1.20"  # ✅ Misty's IP address

# OpenAI API Client (New API Format)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def check_misty_connection():
    """Check if Misty is reachable before running commands."""
    url = f"http://{MISTY_IP}/api/device"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Misty is online and reachable!")
            return True
        else:
            print("⚠️ Misty responded, but there might be an issue:", response.json())
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Misty. Check the IP and network connection.")
        return False

def listen():
    """Captures voice input from the computer’s microphone and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)  # Convert speech to text
        print(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("⚠️ Sorry, I didn't understand.")
        return None
    except sr.RequestError:
        print("❌ Could not request results, check your internet connection.")
        return None

def get_openai_response(user_text):
    """Send text input to OpenAI and return response (New OpenAI API format)"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_text}]
    )
    return response.choices[0].message.content  # ✅ Updated response format

def misty_speak(text):
    """Send text to Misty and make her speak using the correct TTS API."""
    url = f"http://{MISTY_IP}/api/tts/speak"  # ✅ Corrected Misty Speech API
    data = {"text": text, "flush": True}  # "flush": True ensures it interrupts any ongoing speech
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Misty is speaking!")
    else:
        print("❌ Error:", response.json())  # Print full error response for debugging

def main():
    """Full Misty conversation loop with an exit condition."""
    if not check_misty_connection():
        return  # Exit if Misty is not reachable

    while True:
        user_text = listen()  # Step 1: Capture voice input from the computer’s mic
        if user_text:
            ai_response = get_openai_response(user_text)  # Step 2: Get AI response
            misty_speak(ai_response)  # Step 3: Misty speaks the response

        # ✅ Ask user if they want to continue or exit
        user_choice = input("\n🔄 Do you want to ask another question? (yes/no): ").strip().lower()
        if user_choice not in ["yes", "y"]:
            print("👋 Exiting Misty AI Conversation. Have a great day!")
            break  # ✅ Exit the loop

if __name__ == "__main__":
    main()
