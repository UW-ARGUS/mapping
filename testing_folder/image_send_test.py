import socket
import time
import os
import struct
import cv2
import threading

# Configuration
SERVER_IP = '127.0.0.1'
BASE_PORT = 5000
IMAGE_PATHS = ['face1_resize.jpg', 'face2_resize.jpg', 'face3_resize.jpg', 'face4_resize.jpg']
SEND_INTERVAL = 5  # seconds

HEADER_FORMAT = ">dII"  # timestamp (double), flag (uint32), length (uint32)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def send_loop(image_path, port):
    """Continuously sends image to the same port using a persistent socket."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, port))
        print(f"[✓] Connected to port {port} for {image_path}")

        while True:
            if not os.path.exists(image_path):
                print(f"[!] {image_path} does not exist.")
                time.sleep(SEND_INTERVAL)
                continue

            image = cv2.imread(image_path)
            if image is None:
                print(f"[✗] Failed to read {image_path}")
                time.sleep(SEND_INTERVAL)
                continue

            success, encoded_image = cv2.imencode(".jpg", image)
            if not success:
                print(f"[✗] Failed to encode {image_path}")
                time.sleep(SEND_INTERVAL)
                continue

            image_data = encoded_image.tobytes()
            timestamp = time.time()
            length = len(image_data)

            # Prepare header
            header = struct.pack(HEADER_FORMAT, timestamp, port - BASE_PORT, length)

            # Send header + image
            sock.sendall(header + image_data)
            print(f"[⇨] Sent {image_path} ({length} bytes) to port {port}")
            time.sleep(SEND_INTERVAL)

    except Exception as e:
        print(f"[✗] Error on port {port}: {e}")
    finally:
        sock.close()
        print(f"[!] Socket closed on port {port}")

def main():
    for i, image_path in enumerate(IMAGE_PATHS):
        port = BASE_PORT + i
        t = threading.Thread(target=send_loop, args=(image_path, port), daemon=True)
        t.start()

    while True:
        time.sleep(1)  # Keep main thread alive

if __name__ == "__main__":
    main()