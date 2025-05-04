import numpy as np
import torch
import time
import paho.mqtt.publish as publish
from real_time.config import FS, SEGMENT_LEN, THRESHOLD, MODEL_PATH, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
from real_time.preprocessing import apply_eeg_preprocessing

# Load model
model = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
model.eval()

# Replace this function with real EEG stream acquisition
def get_live_eeg_sample():
    # Dummy input (250 x 8)
    return np.random.randn(SEGMENT_LEN, 8)

print("Starting real-time inference loop...")

while True:
    eeg_chunk = get_live_eeg_sample()
    eeg_chunk = apply_eeg_preprocessing(eeg_chunk, fs=FS)
    input_tensor = torch.tensor(eeg_chunk, dtype=torch.float32).unsqueeze(0)  # (1, T, C)
    with torch.no_grad():
        output = model(input_tensor)
        prob = torch.softmax(output, dim=1)[0, 1].item()
        print(f"Prediction prob: {prob:.3f}")
        if prob > THRESHOLD:
            print("Trigger detected! Sending MQTT message: open")
            publish.single(MQTT_TOPIC, payload="open", hostname=MQTT_BROKER, port=MQTT_PORT)
            time.sleep(60)  # wait before allowing next trigger
