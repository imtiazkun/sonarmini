# decoder.py

import sounddevice as sd
import numpy as np
import time
from morse_code import REVERSE_MORSE_CODE_DICT

SAMPLE_RATE = 44100
FRAME_DURATION = 0.05
THRESHOLD = 0.01
FREQ_RANGE = (400, 450)

dot_threshold = 0.25
dash_threshold = 0.5
letter_space_threshold = 0.75
word_space_threshold = 1.5

current_symbol = ""
decoded_message = ""
last_signal_time = None

def detect_dominant_frequency(audio):
    fft = np.fft.fft(audio)
    freqs = np.fft.fftfreq(len(fft), 1 / SAMPLE_RATE)
    fft = np.abs(fft[:len(fft)//2])
    freqs = freqs[:len(freqs)//2]
    return freqs[np.argmax(fft)]

def decode_morse(morse_code):
    words = morse_code.strip().split(" / ")
    decoded = []
    for word in words:
        decoded_word = ''.join(REVERSE_MORSE_CODE_DICT.get(char, '?') for char in word.split())
        decoded.append(decoded_word)
    return ' '.join(decoded)

def callback(indata, frames, time_info, status):
    global current_symbol, decoded_message, last_signal_time

    audio = indata[:, 0]
    amplitude = np.linalg.norm(audio)

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

print("Listening for Morse (400–450Hz)... Press Ctrl+C to stop.")
with sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE, blocksize=int(SAMPLE_RATE * FRAME_DURATION)):
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nFinal Decoded Message:", decoded_message.strip())
