cd downloads/usb_4_mic_array_real

# To run the DOA.py using Mic array on SPOT (you must have Docker installed and turned on)
docker buildx build --platform linux/amd64 -t mic-array-app .
docker save mic-array-app > mic-array-app.tar
scp -P 20022 mic-array-app.tar spot@128.148.140.22:~
ssh -p 20022 spot@128.148.140.22 #password: jI37m1Q5M6y4
sudo docker load < mic-array-app.tar
sudo docker run --rm --privileged mic-array-app 
sudo docker run --rm --privileged --network host mic-array-app

# To run the speech_recog.py on Mac
python3 speech_recog.py
