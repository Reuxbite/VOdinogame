# ...existing code...
import speech_recognition as sr
import sys
import tkinter as tk
from tkinter import ttk

# ...existing code...
import vosk
import sounddevice as sd
import json
import queue
import time
import os

r = sr.Recognizer()
stop_listening = None
mic = None

# map spoken words to numeric commands
COMMAND_MAP = {
    "jump": 1,
    "duck": 0,
    # add more mappings here, e.g. "left": 2, "right": 3
}

def extract_command(text):
    txt = text.lower()
    for word, num in COMMAND_MAP.items():
        if word in txt:
            return word, num
    return None, None

# ...existing code...
def recognize_once_vosk(
    device_index=None,
    model_path=r"C:\Documents\Work\Codes\dino game\vosk-model-small-en-us-0.15",
    duration=3,
    samplerate=16000
):

    if not os.path.isdir(model_path):
        print(f"Vosk model not found at '{model_path}'. Download a model and unpack to that folder.")
        return None

    try:
        model = vosk.Model(model_path)
    except Exception as e:
        print("Failed to load Vosk model:", e)
        return None

    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            # status messages (overflow etc.)
            pass
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=callback, device=device_index):
            rec = vosk.KaldiRecognizer(model, samplerate)
            print(f"Listening (vosk, duration={duration}s)...")
            start_time = time.time()
            recognized_text = ""
            while True:
                try:
                    data = q.get(timeout=0.5)
                except queue.Empty:
                    data = None

                if data:
                    if rec.AcceptWaveform(data):
                        res = rec.Result()
                        try:
                            obj = json.loads(res)
                            recognized_text = obj.get("text", "")
                        except Exception:
                            recognized_text = ""
                    else:
                        # partial = rec.PartialResult()  # optional: inspect partial results
                        pass

                # stop on found command or timeout
                if recognized_text:
                    cmd_name, cmd_val = extract_command(recognized_text)
                    if cmd_name is not None:
                        print(f"You said: {recognized_text}")
                        print(f"Command '{cmd_name}' -> {cmd_val}")
                        return cmd_val
                    else:
                        print(f"You said: {recognized_text} (no command)")
                        return None

                if time.time() - start_time > duration:
                    # Try final result before giving up
                    final = rec.FinalResult()
                    try:
                        obj = json.loads(final)
                        recognized_text = obj.get("text", "")
                    except Exception:
                        recognized_text = ""
                    if recognized_text:
                        cmd_name, cmd_val = extract_command(recognized_text)
                        if cmd_name is not None:
                            print(f"You said: {recognized_text}")
                            print(f"Command '{cmd_name}' -> {cmd_val}")
                            return cmd_val
                        else:
                            print(f"You said: {recognized_text} (no command)")
                    else:
                        print("No speech detected within timeout.")
                    return None
    except Exception as e:
        print("Recording error:", e)
        return None

if __name__ == "__main__":
    # optionally pass device index as command-line arg and optionally model path:
    # python whiteboard.py [device_index] [model_path]
    dev_idx = None
    model_dir = "model"
    if len(sys.argv) > 1:
        try:
            dev_idx = int(sys.argv[1])
        except ValueError:
            dev_idx = None
    if len(sys.argv) > 2:
        model_dir = sys.argv[2]

    result = recognize_once_vosk(device_index=dev_idx, model_path=model_dir, duration=4)
    print("Result (numeric command):", result)
# ...existing code...