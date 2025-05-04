from openai import OpenAI

openai_client = OpenAI(api_key="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")
import paho.mqtt.client as mqtt
import pyttsx3
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr

# === CONFIGURATION ===
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "brain/commands"
OPENAI_API_KEY = "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" 

conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]

# === Initialize TTS ===
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 180)

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# === GUI Setup ===
root = tk.Tk()
root.title("Brain-Controlled ChatGPT")

tk.Label(root, text="Last Command:").pack()
command_label = tk.Label(root, text="", fg="blue", font=("Arial", 12))
command_label.pack()

tk.Label(root, text="Chat History:").pack()
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, state="disabled")
chat_box.pack(padx=10, pady=5)

def update_gui(command, user_msg=None, gpt_reply=None):
    command_label.config(text=command)
    chat_box.config(state="normal")
    if user_msg:
        chat_box.insert(tk.END, f"\nYou: {user_msg}\n")
    if gpt_reply:
        chat_box.insert(tk.END, f"ChatGPT: {gpt_reply}\n")
    chat_box.config(state="disabled")
    chat_box.yview(tk.END)

# === ChatGPT Interaction ===
def chat_with_gpt(user_message):
    conversation_history.append({"role": "user", "content": user_message})
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        speak(reply)  # This line reads out the ChatGPT reply
        update_gui("Response generated", user_message, reply)
    except Exception as e:
        print("ChatGPT error:", e)

# === Command Handler ===
def handle_command(cmd):
    cmd = cmd.lower().strip()
    update_gui(cmd)

    if cmd == "chatgpt":
        print("ChatGPT ready.")
        voice_input()
    elif cmd == "a new response":
        if len(conversation_history) >= 2:
            last_user_msg = conversation_history[-2]["content"]
            chat_with_gpt(last_user_msg)
    elif cmd == "close chatgpt":
        speak("Closing ChatGPT.")
        # root.quit()
    elif cmd.startswith("say "):
        user_msg = cmd[4:]
        chat_with_gpt(user_msg)
    else:
        print(f"Unknown command: {cmd}")

# === MQTT Callback Functions ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connected.")
        client.subscribe(MQTT_TOPIC)
    else:
        print("MQTT connection failed with code", rc)

def on_message(client, userdata, msg):
    command = msg.payload.decode()
    handle_command(command)

# === MQTT Setup ===
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# === Run MQTT in background, GUI in main ===
import threading
mqtt_thread = threading.Thread(target=mqtt_client.loop_forever)
mqtt_thread.daemon = True
mqtt_thread.start()

def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        update_gui("Listening for your question...")
        try:
            audio = recognizer.listen(source, timeout=5)
            user_text = recognizer.recognize_google(audio)
            update_gui("Voice Input Received", user_text)
            chat_with_gpt(user_text)
        except sr.WaitTimeoutError:
            update_gui("No speech detected. Please try again.")
        except sr.UnknownValueError:
            update_gui("Could not understand audio.")
        except Exception as e:
            update_gui(f"Voice input error: {e}")

# Add a button to the GUI for voice input
voice_btn = tk.Button(root, text="Voice Input", command=voice_input)
voice_btn.pack(pady=5)

root.mainloop()