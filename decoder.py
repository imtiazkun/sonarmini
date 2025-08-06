import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from collections import deque
from morse_code import REVERSE_MORSE_CODE_DICT

# --- Config ---
SAMPLE_RATE = 44100
FRAME_DURATION = 0.05  # 50ms
THRESHOLD = 0.01
FREQ_RANGE = (430, 430)

dot_threshold = 0.25
dash_threshold = 0.5
letter_space_threshold = 0.75
word_space_threshold = 1.5

# --- State ---
current_symbol = ""
decoded_message = ""
last_signal_time = None

# --- Visualization State ---
BUFFER_SIZE = int(5 / FRAME_DURATION)  # 5 seconds of rolling amplitude
amplitude_buffer = deque([0]*BUFFER_SIZE, maxlen=BUFFER_SIZE)

# --- Frequency Detection ---
def detect_dominant_frequency(audio):
    fft = np.fft.fft(audio)
    freqs = np.fft.fftfreq(len(fft), 1 / SAMPLE_RATE)
    fft = np.abs(fft[:len(fft)//2])
    freqs = freqs[:len(freqs)//2]
    return freqs[np.argmax(fft)]

# --- Morse Decoding ---
def decode_morse(morse_code):
    words = morse_code.strip().split(" / ")
    decoded = []
    for word in words:
        decoded_word = ''.join(REVERSE_MORSE_CODE_DICT.get(char, '?') for char in word.split())
        decoded.append(decoded_word)
    return ' '.join(decoded)

# --- Audio Callback ---
def callback(indata, frames, time_info, status):
    global current_symbol, decoded_message, last_signal_time

    audio = indata[:, 0]
    amplitude = np.linalg.norm(audio)
    amplitude_buffer.append(amplitude)

    if amplitude > THRESHOLD:
        freq = detect_dominant_frequency(audio)
        if FREQ_RANGE[0] <= freq <= FREQ_RANGE[1]:
            now = time.time()
            if last_signal_time is None:
                last_signal_time = now
            return
    else:
        now = time.time()
        if last_signal_time is not None:
            duration = now - last_signal_time
            if duration < dot_threshold:
                current_symbol += '.'
            elif duration < dash_threshold:
                current_symbol += '-'
            else:
                print(f"[WARN] Long signal ignored: {duration:.2f}s")
            last_signal_time = None

        if current_symbol:
            silence_duration = now - last_signal_time if last_signal_time else 0
            if silence_duration > letter_space_threshold:
                print(f"Symbol: {current_symbol}")
                decoded_message += REVERSE_MORSE_CODE_DICT.get(current_symbol, '?')
                current_symbol = ""

            if silence_duration > word_space_threshold:
                decoded_message += ' '
                print(f"[WORD GAP] {decoded_message.strip()}")

# --- Live Plotting ---
fig, ax = plt.subplots()
x = np.linspace(-BUFFER_SIZE * FRAME_DURATION, 0, BUFFER_SIZE)
line, = ax.plot(x, [0]*BUFFER_SIZE)
ax.set_ylim(0, 0.05)
ax.set_xlim(-BUFFER_SIZE * FRAME_DURATION, 0)
ax.set_title("Real-time Audio Amplitude")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")

def update_plot(frame):
    line.set_ydata(amplitude_buffer)
    return line,

print("Listening for Morse (400–480Hz)... Close the plot window or press Ctrl+C to stop.")

stream = sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE, blocksize=int(SAMPLE_RATE * FRAME_DURATION))

with stream:
    ani = animation.FuncAnimation(fig, update_plot, interval=50, blit=True)
    try:
        plt.show()
    except KeyboardInterrupt:
        pass

print("\nFinal Decoded Message:", decoded_message.strip())
