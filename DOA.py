from tuning import Tuning
import usb.core
import usb.util
import time
import socket
import sys
import threading

# Check for SPOT IP argument
if len(sys.argv) < 2:
    print("Usage: python3 DOA.py <SPOT_IP>")
    sys.exit(1)

SPOT_IP = sys.argv[1]
SPOT_PORT = 5005  # You can change this port if needed

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

def direction_monitoring(Mic_tuning, sock, SPOT_IP, SPOT_PORT):
    while True:
        try:
            direction = Mic_tuning.direction
            print(f"Current direction: {direction}")
            msg = f"Direction: {direction}"
            sock.sendto(msg.encode(), (SPOT_IP, SPOT_PORT))
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped by user.")
            break

def udp_receiver(SPOT_PORT):
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Binding UDP receiver to port", SPOT_PORT)
    recv_sock.bind(("", SPOT_PORT))
    print("Waiting for messages from Mac...")
    try:
        while True:
            data, addr = recv_sock.recvfrom(1024)
            print(f"Received from {addr}: {data.decode()}")
    except KeyboardInterrupt:
        print("UDP receiver stopped.")

if dev:
    Mic_tuning = Tuning(dev)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Starting direction monitoring and UDP sending to SPOT...")

    # Start both threads
    t1 = threading.Thread(target=direction_monitoring, args=(Mic_tuning, sock, SPOT_IP, SPOT_PORT))
    t2 = threading.Thread(target=udp_receiver, args=(SPOT_PORT,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
else:
    print("Mic array not found.")