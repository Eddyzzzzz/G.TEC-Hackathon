FS = 250
WINDOW_SEC = 0.4
SEGMENT_LEN = int(FS * WINDOW_SEC)
THRESHOLD = 0.15  # from val tuning
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "brain/commands"
MODEL_PATH = "model_checkpoints/best_model.pt"