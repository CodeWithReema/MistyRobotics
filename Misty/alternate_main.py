# Import necessary libraries
import requests  # Used for making HTTP requests to Misty's API
import openai  # OpenAI's API for generating responses
import os  # Provides functions to interact with the operating system
import speech_recognition as sr  # Library for speech recognition
import time  # Provides time-related functions
from dotenv import load_dotenv  # Loads environment variables from a .env file

# Load environment variables from a .env file (containing the OpenAI API key)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Retrieves the OpenAI API key from environment variables

# ✅ Misty's local network IP address (Ensure it is correct for connection)
MISTY_IP = "192.168.1.20"  

# Initialize OpenAI API client using the latest API format
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Default movement speeds for Misty
DEFAULT_LINEAR_VELOCITY = 1.0  # Movement speed when Misty moves forward
DEFAULT_ANGULAR_VELOCITY = 70  # Rotation speed when Misty turns

def check_misty_connection():
    """Check if Misty is online and reachable via HTTP request."""
    url = f"http://{MISTY_IP}/api/device"  # Endpoint to check Misty's status

    try:
        response = requests.get(url, timeout=5)  # Sends a GET request with a timeout of 5 seconds
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
    """Continuously listens for voice input and only processes commands when 'Hey Misty' is detected."""
    recognizer = sr.Recognizer()  # Initialize speech recognition
    with sr.Microphone() as source:  # Use the default microphone as the input source
        while True:
            print("🎤 Listening... Say 'Hey Misty' to activate.")
            recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
            audio = recognizer.listen(source)  # Listen for speech input

            try:
                text = recognizer.recognize_google(audio).lower()  # Convert speech to lowercase text
                print(f"🗣️ You said: {text}")

                if "hey misty" in text:  # Check if the wake word is present
                    command = text.replace("hey misty", "").strip()  # Remove wake word and clean up
                    return command if command else None  # Return command if available
                else:
                    print("⚠️ No wake word detected. Continuing to listen...")
            except sr.UnknownValueError:
                print("⚠️ Could not understand. Listening again...")
            except sr.RequestError:
                print("❌ Could not request results. Check internet connection.")
                return None

def misty_move(command):
    """Make Misty move forward for a given number of seconds if a valid command is detected."""
    words = command.split()  # Split command into individual words

    # Ensure the command format is: "move <time> seconds"
    if len(words) >= 3 and words[0] == "move" and words[2] == "seconds":
        try:
            duration = float(words[1])  # Convert the second word into a number
            url = f"http://{MISTY_IP}/api/drive"  # Endpoint to send movement commands
            data = {"linearVelocity": DEFAULT_LINEAR_VELOCITY, "angularVelocity": 0}  # Move forward
            headers = {"Content-Type": "application/json"}  # Set request headers
            
            requests.post(url, json=data, headers=headers)  # Send movement command to Misty
            print(f"✅ Moving Misty forward for {duration} seconds.")
            time.sleep(duration)  # Wait for the duration before stopping

            # Stop Misty after the movement duration ends
            stop_data = {"linearVelocity": 0, "angularVelocity": 0}  # Stop movement
            requests.post(url, json=stop_data, headers=headers)  # Send stop command
            print("⏹️ Stopping Misty.")
            return True
        except ValueError:
            print("⚠️ Invalid duration format.")  # Handle invalid number errors
            return False
    return False  # If the command format is incorrect, return False

def get_openai_response(user_text):
    """Send the user's text input to OpenAI and return the AI-generated response."""
    response = client.chat.completions.create(
        model="gpt-4",  # Use GPT-4 model
        messages=[{"role": "user", "content": user_text}]  # Provide user input as a conversation message
    )
    return response.choices[0].message.content  # Extract and return AI's response

def misty_speak(text):
    """Send text to Misty to make her speak the given message."""
    url = f"http://{MISTY_IP}/api/tts/speak"  # Misty's text-to-speech API endpoint
    data = {"text": text, "flush": True}  # Prepare request data with text to speak
    headers = {"Content-Type": "application/json"}  # Set request headers
    requests.post(url, json=data, headers=headers)  # Send request to Misty to speak

def main():
    """Main function: Runs a continuous loop where Misty listens, processes commands, and responds."""
    if not check_misty_connection():  # Check if Misty is online before starting
        return  # Exit if Misty is unreachable

    while True:
        user_text = listen()  # Wait for the user to speak a command
        if user_text:  # If a valid command is given
            if misty_move(user_text):  # Try executing a movement command
                continue  # Skip to the next iteration if movement was successful
            
            ai_response = get_openai_response(user_text)  # Get an AI-generated response
            misty_speak(ai_response)  # Have Misty speak the response

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
