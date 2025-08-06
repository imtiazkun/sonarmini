# encoder.py

import numpy as np
import sounddevice as sd
import time
from morse_code import MORSE_CODE_DICT

FREQUENCY = 430  # Hz
SAMPLE_RATE = 44100

DOT_DURATION = 0.2
DASH_DURATION = DOT_DURATION * 3
SYMBOL_SPACE = DOT_DURATION
LETTER_SPACE = DOT_DURATION * 3
WORD_SPACE = DOT_DURATION * 7

def beep(duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * FREQUENCY * t)
    sd.play(wave, samplerate=SAMPLE_RATE)
    sd.wait()

def send_morse(message):
    message = message.upper()
    for char in message:
        if char not in MORSE_CODE_DICT:
            continue
        morse = MORSE_CODE_DICT[char]
        for symbol in morse:
            if symbol == '.':
                beep(DOT_DURATION)
            elif symbol == '-':
                beep(DASH_DURATION)
            time.sleep(SYMBOL_SPACE)
        time.sleep(LETTER_SPACE - SYMBOL_SPACE)
    time.sleep(WORD_SPACE)

if __name__ == "__main__":
    msg = input("Enter message to send: ")
    send_morse(msg)
