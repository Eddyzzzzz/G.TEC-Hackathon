# Brain-Controlled ChatGPT

A real-time EEG-based intent detector that triggers a ChatGPT voice assistant via MQTT.

## Results 

<p align="left">
  <a href="https://docs.google.com/presentation/d/1ATDAViMGEZEGJ7OFfEbvGqKSl-iMVAZM/edit?usp=sharing&ouid=114411754495736577659&rtpof=true&sd=true" target="_blank">
    <img src="https://img.shields.io/badge/View%20Presentation-blue?style=for-the-badge" alt="View Presentation">
  </a>
  &nbsp;
  <a href="https://drive.google.com/file/d/1VJSqVCjtSaDPo2jxpAOs2tgSBSYcSG3M/view?usp=sharing" target="_blank">
    <img src="https://img.shields.io/badge/View%20Demo-green?style=for-the-badge" alt="View Demo">
  </a>
</p>

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

## Achnowledgements

This project was developed during [BR41N.IO Spring School 2025](https://www.br41n.io/Spring-School-2025).
