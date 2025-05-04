# Brain-Controlled ChatGPT

A real-time EEG-based intent detector that triggers a ChatGPT voice assistant via MQTT.

## Setup

```bash
pip install -r requirements.txt
brew install portaudio  # for macOS
pip install pyaudio
```
## Run

In Terminal 1 (EEG trigger loop):
```bash
python3 runner.py
```

In Terminal 2 (GUI + ChatGPT):
```bash
python3 app.py
```

## Notes
- runner.py simulates EEG data → detects trigger → sends "open" via MQTT.
- app.py receives "open" → activates voice input → sends to ChatGPT → reads reply.
- Requires OpenAI API key in app.py.
