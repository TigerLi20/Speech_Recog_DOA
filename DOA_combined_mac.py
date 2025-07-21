from tuning import Tuning
import usb.core
import usb.util
import time
import sys
import sounddevice as sd
import numpy as np
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
import whisper
from scipy.io.wavfile import write
from scipy.signal import resample
import os

# --- DOA Setup ---
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

if dev is None:
    print("ERROR: Mic array USB device not found. Please check the connection and try again.")
    sys.exit(1)

Mic_tuning = Tuning(dev)
print(f"Initial direction: {Mic_tuning.direction}")

# --- Whisper Setup ---
model = whisper.load_model("base.en")

# --- Audio Config ---
try:
    default_device_index = sd.default.device[0]
    default_input_device = sd.query_devices(default_device_index)
    INPUT_SAMPLE_RATE = int(default_input_device['default_samplerate'])
except Exception:
    INPUT_SAMPLE_RATE = 16000  # fallback
WHISPER_SAMPLE_RATE = 16000
CHUNK_DURATION = 5  # seconds
CHUNK_SIZE = INPUT_SAMPLE_RATE * CHUNK_DURATION
SILENCE_THRESHOLD = 0.03  # Lowered threshold to pick up softer sounds
SILENCE_TIMEOUT = 20
DEFAULT_TRANSCRIPTION = "Find index of all objects that can be manipulated by one hand."

audio_buffer = []
voice_detected = False

def callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    audio_data = indata[:, 0]
    audio_buffer.extend(audio_data)

def is_silent(audio_data):
    max_amplitude = np.max(np.abs(audio_data))
    # sprint(f"Max Amplitude: {max_amplitude}")
    return max_amplitude < SILENCE_THRESHOLD

def resample_audio(audio, input_rate, target_rate):
    num_samples = int(len(audio) * target_rate / input_rate)
    return resample(audio, num_samples)

def main():
    global voice_detected
    print("Starting live transcription and DOA direction detection (Mac version)...")
    try:
        with sd.InputStream(samplerate=INPUT_SAMPLE_RATE, channels=1, callback=callback, dtype="float32"):
            last_voice_time = time.time()
            while True:
                # Print current direction every second
                direction = Mic_tuning.direction
                print(f"Current direction: {direction}")
                time.sleep(1)
                if len(audio_buffer) >= CHUNK_SIZE:
                    audio_chunk = np.array(audio_buffer[:CHUNK_SIZE])
                    del audio_buffer[:CHUNK_SIZE]
                    audio_chunk_resampled = resample_audio(audio_chunk, INPUT_SAMPLE_RATE, WHISPER_SAMPLE_RATE)
                    if is_silent(audio_chunk_resampled) and not voice_detected:
                        print("Silence detected.")
                        if not voice_detected and time.time() - last_voice_time > SILENCE_TIMEOUT:
                            print(f"No voice input detected. Default transcription: {DEFAULT_TRANSCRIPTION}")
                            print(f"Direction: {direction}")
                            break
                    else:
                        voice_detected = True
                        temp_wav = "/tmp/.temp_audio.wav"
                        scaled_audio = (audio_chunk_resampled * 32767).astype(np.int16)
                        write(temp_wav, WHISPER_SAMPLE_RATE, scaled_audio)
                        if not is_silent(audio_chunk_resampled):
                            last_voice_time = time.time()
                            result = model.transcribe(temp_wav)
                            transcription = result['text']
                            print(f"Transcription: {transcription}")
                            print(f"Direction: {direction}")
                        if time.time() - last_voice_time > SILENCE_TIMEOUT:
                            break
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
