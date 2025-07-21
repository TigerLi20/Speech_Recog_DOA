from tuning import Tuning
import usb.core
import usb.util
import time
import sys
import socket
import sounddevice as sd
import numpy as np
import whisper
from scipy.io.wavfile import write
from scipy.signal import resample
import os

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

if dev is None:
    print("ERROR: Mic array USB device not found. Please check the connection and try again.")
    sys.exit(1)

if len(sys.argv) != 2:
    print("Usage: sudo python3 DOA.py <SPOT_IP>")
    sys.exit(1)

spot_ip = sys.argv[1]
PORT = 5005  # You can change this port if needed

# Set up UDP socket to send direction data to SPOT
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if dev:
    Mic_tuning = Tuning(dev)
    print(Mic_tuning.direction)
    # Whisper model setup
    model = whisper.load_model("base.en")

    # Audio configuration
    try:
        default_device_index = sd.default.device[0]
        default_input_device = sd.query_devices(default_device_index)
        INPUT_SAMPLE_RATE = int(default_input_device['default_samplerate'])
    except Exception:
        INPUT_SAMPLE_RATE = 16000  # fallback
    WHISPER_SAMPLE_RATE = 16000
    CHUNK_DURATION = 5  # seconds
    CHUNK_SIZE = INPUT_SAMPLE_RATE * CHUNK_DURATION
    SILENCE_THRESHOLD = 0.03
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
        print(f"Max Amplitude: {max_amplitude}")
        return max_amplitude < SILENCE_THRESHOLD

    def resample_audio(audio, input_rate, target_rate):
        num_samples = int(len(audio) * target_rate / input_rate)
        return resample(audio, num_samples)

    def transcribe_and_send():
        global voice_detected
        print("Starting live transcription and DOA direction detection...")
        try:
            with sd.InputStream(device=6, samplerate=INPUT_SAMPLE_RATE, channels=1, callback=callback, dtype="float32"):
                last_voice_time = time.time()
                while True:
                    if len(audio_buffer) >= CHUNK_SIZE:
                        audio_chunk = np.array(audio_buffer[:CHUNK_SIZE])
                        del audio_buffer[:CHUNK_SIZE]
                        audio_chunk_resampled = resample_audio(audio_chunk, INPUT_SAMPLE_RATE, WHISPER_SAMPLE_RATE)
                        if is_silent(audio_chunk_resampled) and not voice_detected:
                            print("Silence detected.")
                            if not voice_detected and time.time() - last_voice_time > SILENCE_TIMEOUT:
                                print("No voice input detected. Sending default transcription.")
                                direction = Mic_tuning.direction
                                msg = f"{DEFAULT_TRANSCRIPTION}|{direction}"
                                print(msg)
                                sock.sendto(msg.encode(), (spot_ip, PORT))
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
                                direction = Mic_tuning.direction
                                msg = f"{transcription}|{direction}"
                                print(msg)
                                sock.sendto(msg.encode(), (spot_ip, PORT))
                            if time.time() - last_voice_time > SILENCE_TIMEOUT:
                                break
        except KeyboardInterrupt:
            print("\nStopped.")
        except Exception as e:
            print(f"Error: {e}")

    def clear_transcription(filename="/tmp/.transcriptions.txt"):
        # Only clear if file exists
        if os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")

    def save_transcription(transcription, filename="/tmp/.transcriptions.txt"):
        # Only save if file exists
        if os.path.exists(filename):
            with open(filename, "a") as f:
                f.write(transcription + "\n")

    if __name__ == "__main__":
        transcribe_and_send()
