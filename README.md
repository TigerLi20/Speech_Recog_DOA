# ReSpeaker USB 4 Mic Array Integration for LEGS-POMDP

This directory contains code, scripts, and instructions for using the ReSpeaker USB 4 Mic Array with the LEGS-POMDP project. It includes tools for audio capture, speech recognition, direction-of-arrival (DOA) estimation, and integration with the SPOT robot platform.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
  - [Running DOA on SPOT (Docker)](#running-doa-on-spot-docker)
  - [Running Speech Recognition on Mac](#running-speech-recognition-on-mac)
- [Notes](#notes)
- [References](#references)
- [Contact](#contact)

---

## Overview

This branch provides a complete toolkit for working with the ReSpeaker USB 4 Mic Array, including:
- Real-time speech recognition using OpenAI's Whisper
- Audio capture and processing
- DOA estimation
- Integration scripts for sending results to the SPOT robot

---

## Features

- **4-microphone USB array** with 12 programmable RGB LEDs
- Built-in audio processing: AEC, VAD, DOA, Beamforming, Noise Suppression
- 16kHz sample rate
- Dockerized deployment for SPOT robot
- Real-time speech-to-text using Whisper
- UDP communication with SPOT robot

---

## Directory Structure

```
usb_4_mic_array_real/
├── Dockerfile
├── DOA.py
├── DOA_combined_mac.py
├── speech_recog.py
├── requirements.txt
├── test/
│   └── (test audio/scripts)
├── firmware/
│   └── (firmware update scripts)
├── .tmp/
│   └── (temporary files, e.g., .temp_audio.wav)
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/h2r/LEGS-POMDP.git
cd usb_4_mic_array_real
```

### 2. Install Dependencies (on Mac)

```sh
pip install -r requirements.txt
```

- You will need [Docker](https://www.docker.com/) installed for SPOT deployment.
- For Whisper, the model will be downloaded automatically on first run.

---

## Usage

### Running DOA.py using Mic Array on SPOT (Docker)

You must have Docker installed and running.  
Replace `spot@128.148.140.22` and password as needed for your SPOT robot.

```sh
cd downloads/usb_4_mic_array_real

# Build Docker image for amd64
docker buildx build --platform linux/amd64 -t mic-array-app .

# Save Docker image to tar
docker save mic-array-app > mic-array-app.tar

# Copy image to SPOT robot
scp -P 20022 mic-array-app.tar spot@128.148.140.22:~

# SSH into SPOT
ssh -p 20022 spot@128.148.140.22 # password: jI37m1Q5M6y4

# On SPOT, load and run the container
sudo docker load < mic-array-app.tar
sudo docker run --rm --privileged mic-array-app
sudo docker run --rm --privileged --network host mic-array-app
```

### Running Speech Recognition on Mac

```sh
python3 speech_recog.py
```

- This script uses your default microphone and OpenAI Whisper to transcribe speech in real time.
- Transcriptions are sent to the SPOT robot via UDP.

---

## Notes

- **Large files** (e.g., Whisper models, firmware binaries) have been removed from the repository to comply with GitHub's size limits. Download them separately as needed.
- The `.tmp/` directory is used for temporary files and will be created automatically.
- For full hardware documentation, see the [ReSpeaker USB 4 Mic Array Wiki](https://wiki.seeedstudio.com/ReSpeaker_USB_Mic_Array/).

---

## References

- [ReSpeaker USB 4 Mic Array Wiki](https://wiki.seeedstudio.com/ReSpeaker_USB_Mic_Array/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Docker Documentation](https://docs.docker.com/)

---

## Contact

**Maintainer:** Tiger Li  
**For issues:** [GitHub Issues](https://github.com/h2r/LEGS-POMDP/issues)

---
