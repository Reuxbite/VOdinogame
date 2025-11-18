import threading, queue

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except Exception as e:
    print("[VOICE] Missing dependencies:", e)
    VOICE_AVAILABLE = False

command_queue = queue.Queue()
voice_ready = False
listening = True

# Define wake words that trigger the jump command
WAKE_WORDS = ["jump", "jump dino", "dino jump"]


def _voice_loop():
    global voice_ready

    if not VOICE_AVAILABLE:
        print("[VOICE] Not available.")
        return

    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        # Adjust for ambient noise
        print("[VOICE] Calibrating microphone for ambient noise...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        voice_ready = True
        print("[VOICE] Listening for wake words:", WAKE_WORDS)

        while listening:
            try:
                with microphone as source:
                    # Listen for audio with timeout
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                
                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio).lower()
                print(f"[VOICE HEARD] {text}")
                
                # Check if any wake word is in the heard text
                for wake_word in WAKE_WORDS:
                    if wake_word in text:
                        print(f"[VOICE DETECTED] Wake word detected: {wake_word}")
                        command_queue.put("jump")
                        break

            except sr.WaitTimeoutError:
                # No speech detected in timeout period - this is normal
                pass
            except sr.UnknownValueError:
                # Speech was unintelligible
                pass
            except sr.RequestError as e:
                # API error
                print(f"[VOICE ERROR] Could not request results from Google Speech Recognition service: {e}")
            except Exception as e:
                # Other errors
                print(f"[VOICE ERROR] Unexpected error: {e}")

    except Exception as e:
        print("[VOICE ERROR] Failed to initialize:", e)

    finally:
        voice_ready = False
        print("[VOICE] Listener stopped.")


def start_listening():
    t = threading.Thread(target=_voice_loop, daemon=True)
    t.start()
