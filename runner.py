import numpy as np
import torch
import time
import paho.mqtt.client as mqtt
from real_time_decoding.config import FS, SEGMENT_LEN, THRESHOLD, MODEL_PATH, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
from real_time_decoding.preprocessing import apply_eeg_preprocessing
from real_time_decoding.models import CNN1

# Load model
model = CNN1(Chans=8, Samples=SEGMENT_LEN)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

def get_live_eeg_sample():
    # Simulate real-time EEG segment (0.4s at 250 Hz, 8 channels)
    return np.random.randn(SEGMENT_LEN, 8)

if __name__ == "__main__":
    print("Starting real-time dummy EEG inference...")

    while True:
        eeg_chunk = get_live_eeg_sample()
        eeg_chunk = apply_eeg_preprocessing(eeg_chunk, fs=FS)
        input_tensor = torch.tensor(eeg_chunk, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            output = model(input_tensor)
            prob = torch.softmax(output, dim=1)[0, 1].item()
            print(f"Prediction prob: {prob:.3f}")

            if prob > THRESHOLD:
                print("Trigger detected! Sending MQTT message: open")
                mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
                mqtt_client.publish(MQTT_TOPIC, payload="open")
                mqtt_client.disconnect()
                time.sleep(120) # trigger cooldown: sleep to avoid repeated triggers

        time.sleep(0.4)  # simulate real-time buffer interval, waits for 0.4 seconds 