
import os, threading, queue
import numpy as np

try:
    import pyaudio
    import torch
    from vosk import Model, KaldiRecognizer
    import json
    VOICE_AVAILABLE = True
except Exception as e:
    print("[VOICE] Missing dependencies:", e)
    VOICE_AVAILABLE = False

command_queue = queue.Queue()
voice_ready = False
listening = True

# Audio settings for Vosk (16kHz required)
SAMPLE_RATE = 16000
CHUNK_SIZE = 512


def _voice_loop():
    global voice_ready

    if not VOICE_AVAILABLE:
        print("[VOICE] Not available.")
        return

    try:
        # Load Silero VAD model
        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                       model='silero_vad',
                                       force_reload=False,
                                       onnx=False)
        (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
        
        # Check for Vosk model
        vosk_model_path = "vosk-model"
        if not os.path.exists(vosk_model_path):
            print(f"[VOICE] ERROR: Vosk model not found at '{vosk_model_path}'")
            print("[VOICE] Please download a Vosk model from https://alphacephei.com/vosk/models")
            print("[VOICE] Extract it and rename the folder to 'vosk-model' in the project root")
            return
        
        # Initialize Vosk recognizer
        vosk_model = Model(vosk_model_path)
        recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
        recognizer.SetWords(True)
        
        print("[VOICE] Silero VAD and Vosk loaded successfully")

        # Initialize PyAudio
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )

        voice_ready = True
        print("[VOICE] Listening for speech (say 'jump' to make dino jump)...")

        # Buffer to accumulate audio when speech is detected
        audio_buffer = []
        is_speaking = False
        frames_after_speech = 0
        FRAMES_TO_RECORD = int(0.5 * SAMPLE_RATE / CHUNK_SIZE)  # ~0.5 seconds worth of frames

        while listening:
            # Read audio chunk
            pcm_data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            
            # Convert to numpy array for Silero VAD (float32, normalized)
            audio_int16 = np.frombuffer(pcm_data, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            audio_tensor = torch.from_numpy(audio_float32)
            
            # Get speech probability from Silero VAD
            speech_prob = model(audio_tensor, SAMPLE_RATE).item()
            
            # Detect speech start
            if speech_prob > 0.6 and not is_speaking:
                is_speaking = True
                audio_buffer = [pcm_data]
                frames_after_speech = 0
                print(f"[VAD] Speech detected (prob: {speech_prob:.2f})")
            
            # Continue recording while speaking or for a short period after
            elif is_speaking:
                audio_buffer.append(pcm_data)
                frames_after_speech += 1
                
                # After recording enough frames (~0.5s), process with Vosk
                if frames_after_speech >= FRAMES_TO_RECORD:
                    is_speaking = False
                    
                    # Concatenate all audio chunks
                    full_audio = b''.join(audio_buffer)
                    
                    # Feed to Vosk recognizer
                    if recognizer.AcceptWaveform(full_audio):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").lower()
                    else:
                        result = json.loads(recognizer.PartialResult())
                        text = result.get("partial", "").lower()
                    
                    if text:
                        print(f"[VOICE TRANSCRIBED] '{text}'")
                        
                        # Check if "jump" is in the transcribed text
                        if "jump" in text:
                            print("[VOICE] Jump command detected!")
                            command_queue.put("jump")
                    
                    # Reset recognizer for next utterance
                    recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
                    recognizer.SetWords(True)
                    audio_buffer = []

    except Exception as e:
        print("[VOICE ERROR]:", e)
        import traceback
        traceback.print_exc()

    finally:
        voice_ready = False
        try:
            stream.stop_stream()
            stream.close()
            pa.terminate()
        except Exception:
            pass
        print("[VOICE] Listener stopped.")


def start_listening():
    t = threading.Thread(target=_voice_loop, daemon=True)
    t.start()
