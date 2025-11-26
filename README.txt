VOdinogame

Quick overview
- A simple voice-controlled Dino runner using Pygame and Picovoice Porcupine for wake-word detection.

Requirements
- Python 3.8+ (3.10+ recommended)
- Packages listed in `requirements.txt`:
  - `pygame`
  - `pvporcupine`
  - `PyAudio` (microphone I/O)

Install (PowerShell)
1. Upgrade pip (optional):
   python -m pip install --upgrade pip
2. Install requirements:
   pip install -r requirements.txt


Configuration
- `settings.py` contains tuning values you may want to change:
  - `PV_ACCESS_KEY` — set to your PicoVoice access key (project will not start voice listener without a valid key).
  - `DEFAULT_KEYWORDS` / `Keywords/` folder — contains `.ppn` models or built-in keywords.
  - `JUMP_COOLDOWN` — milliseconds between voice-triggered jumps.
  - `CACTUS_HITBOX_SHRINK` — (width_shrink, height_shrink) to tighten obstacle collision boxes.
  - `frames_per_buffer` in `voice_control.py` — smaller values lower latency (e.g., 128 or 64), but raise CPU usage.

Running the game
- From project root (PowerShell):
  python .\main.py

Controls
- Space: manual jump
- V: toggle voice mode on/off

Troubleshooting & tips
- If voice detection causes stutter during obstacle spawns:
  - Ensure `voice_control.py` uses a bounded queue (it does by default) so the audio thread does not block.
  - Reduce console prints — console I/O can slow down the main loop and audio thread.
- If voice feels sluggish:
  - Reduce `frames_per_buffer` in `voice_control.py` to 64 (lower latency, more CPU).
  - Lower `JUMP_COOLDOWN` in `settings.py` to allow faster successive voice jumps.
- If you get false collisions:
  - Increase `CACTUS_HITBOX_SHRINK` values to make collision rect smaller.

Debugging ideas
- Draw collision rects temporarily (add code in `main.py`) to visually tune hitbox values.
- Use `pipwin` to install `PyAudio` on Windows reliably.

License / Notes
- This repository includes uses of third-party packages. Follow their licenses.
- Picovoice (Porcupine) requires an access key — the project includes a placeholder in `settings.py`.
