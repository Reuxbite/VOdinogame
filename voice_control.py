import pvporcupine
import os, threading, queue
from settings import DEFAULT_KEYWORDS, PV_ACCESS_KEY

try:
    import pvporcupine, pyaudio, struct
    VOICE_AVAILABLE = True
except Exception as e:
    print("[VOICE] Missing dependencies:", e)
    VOICE_AVAILABLE = False

# Bounded queue to avoid unbounded growth and reduce contention
command_queue = queue.Queue(maxsize=10)
voice_ready = False
listening = True


def _voice_loop():
    global voice_ready

    if not VOICE_AVAILABLE:
        print("[VOICE] Not available.")
        return

    if not PV_ACCESS_KEY or PV_ACCESS_KEY == "YOUR_ACCESS_KEY_HERE":
        print("[VOICE] ERROR: Access key missing. Add it in settings.py (PV_ACCESS_KEY).")
        return

    try:
        keyword_dir = "Keywords"
        keyword_paths = []

        if os.path.isdir(keyword_dir):
            for f in sorted(os.listdir(keyword_dir)):
                if f.lower().endswith(".ppn"):
                    keyword_paths.append(os.path.join(keyword_dir, f))

        if keyword_paths:
            porcupine = pvporcupine.create(
                keyword_paths=keyword_paths,
                access_key=PV_ACCESS_KEY
            )
            keyword_names = [os.path.splitext(os.path.basename(p))[0] for p in keyword_paths]
            print("[VOICE] Loaded custom .ppn models:", keyword_names)
        else:
            porcupine = pvporcupine.create(
                keywords=DEFAULT_KEYWORDS,
                access_key=PV_ACCESS_KEY
            )
            keyword_names = DEFAULT_KEYWORDS
            print("[VOICE] Using built-in keywords:", keyword_names)

        # Initialize microphone
        pa = pyaudio.PyAudio()
        # Smaller frames_per_buffer reduces detection latency (slightly higher CPU)
        frames_per_buffer = 64
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=frames_per_buffer
        )

        voice_ready = True
        print("[VOICE] Listening for:", keyword_names)

        while listening:
            pcm = stream.read(512, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * 512, pcm)
            index = porcupine.process(pcm)
            if index >= 0:
                keyword = keyword_names[index]
                print(f"[VOICE DETECTED] {keyword}")
                try:
                    # try non-blocking enqueue; drop if queue is full to avoid blocking audio thread
                    command_queue.put_nowait(keyword)
                except queue.Full:
                    # drop the detection if main thread is too slow; prefer audio continuity
                    pass

    except Exception as e:
        print("[VOICE ERROR]:", e)

    finally:
        voice_ready = False
        try:
            stream.stop_stream()
            stream.close()
            pa.terminate()
        except Exception:
            pass
        try:
            porcupine.delete()
        except Exception:
            pass
        print("[VOICE] Listener stopped.")


def start_listening():
    t = threading.Thread(target=_voice_loop, daemon=True)
    t.start()
