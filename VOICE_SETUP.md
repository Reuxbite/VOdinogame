# Voice Control Setup Guide

## Overview
This game now uses **Silero VAD** (Voice Activity Detection) + **Vosk** (offline speech recognition) instead of Porcupine for voice control.

## Dependencies
Install the following Python packages:

```bash
pip install torch numpy pyaudio vosk
```

## Vosk Model Setup
1. Download a Vosk model from: https://alphacephei.com/vosk/models
2. Recommended: `vosk-model-small-en-us-0.15` (lightweight English model)
3. Extract the downloaded zip file
4. Rename the extracted folder to `vosk-model`
5. Place it in the project root directory (same level as main.py)

## How It Works

### Voice Activity Detection (VAD)
- Silero VAD continuously monitors audio input
- When speech probability > 0.6, it starts recording
- Records approximately 0.5 seconds of audio

### Speech Recognition
- Recorded audio is sent to Vosk KaldiRecognizer (16000 Hz)
- Transcribes the audio to text
- If the text contains "jump", the command is sent to the game

### Game Integration
- Same interface as before: `start_listening()`, `command_queue`, `voice_ready`
- Say "jump" to make the dino jump
- Press 'V' key to toggle voice mode on/off

## Troubleshooting

### "Vosk model not found"
Make sure the `vosk-model` folder is in the correct location:
```
VOdinogame/
├── main.py
├── voice_control.py
├── vosk-model/          ← This folder should be here
│   ├── am/
│   ├── conf/
│   ├── graph/
│   └── ...
```

### Audio Issues
- Check your microphone permissions
- Ensure no other application is using the microphone
- Try adjusting the VAD threshold in voice_control.py (line 86): `if speech_prob > 0.6`

### Performance
- The first run may be slower as PyTorch downloads the Silero VAD model
- Vosk processes audio offline, so no internet connection is required during gameplay

## Advantages Over Porcupine
- ✅ No API key required
- ✅ Fully offline operation
- ✅ Recognizes natural speech (not just wake words)
- ✅ More flexible - can detect any word, not just predefined keywords
- ✅ Open source and free
