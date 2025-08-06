import sounddevice as sd
import numpy as np
from datetime import datetime
import os

# --- Configuration ---
SAMPLE_RATE = 44100         # CD-quality
FRAME_DURATION = 0.5        # seconds per frame
LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "log.txt")

# --- Setup ---
os.makedirs(LOG_FOLDER, exist_ok=True)

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    line = f"[{get_timestamp()}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def detect_dominant_frequency(audio_data):
    # Apply FFT and find the peak frequency
    fft = np.fft.fft(audio_data)
    fft = np.abs(fft[:len(fft)//2])  # only positive frequencies
    freqs = np.fft.fftfreq(len(audio_data), d=1/SAMPLE_RATE)
    freqs = freqs[:len(freqs)//2]
    peak_freq = freqs[np.argmax(fft)]
    return abs(peak_freq)

def main():
    log("Starting frequency logger...")
    while True:
        try:
            duration = FRAME_DURATION
            audio = sd.rec(int(SAMPLE_RATE * duration), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()

            freq = detect_dominant_frequency(audio)
            log(f"Detected frequency: {freq:.2f} Hz")

        except KeyboardInterrupt:
            log("Stopping logger.")
            break
        except Exception as e:
            log(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
