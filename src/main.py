"""
ARGUS 3D mapping reconstruction.
"""

import cv2
from modules.image_data import ImageData
from modules.image_receiver.image_receiver_manager import ImageReceiverManager
from utilities.message_queue import MessageQueue
import os
import fcntl

SHARED_DIR = '../../gui/src/assets'
TEMP_DIR = './temp'
LOCK_FILE = os.path.join(SHARED_DIR, "batch.lock")

def main() -> int:
    """
    Main function.
    """
    # TODO: These values should come from a config file
    base_port = 5000
    number_of_connections = 4
    image_to_mapping_queue = MessageQueue[ImageData](maxsize=100)

    image_receiver_manager = ImageReceiverManager(
        base_port=base_port,
        number_of_connections=number_of_connections,
        image_queue=image_to_mapping_queue,
    )

    os.makedirs(SHARED_DIR, exist_ok=True)

    try:
        image_receiver_manager.start_workers()

        while True:

            with open(LOCK_FILE, 'r+') as lock_file:

                fcntl.flock(lock_file, fcntl.LOCK_EX)
                try:
                    print("🔒 Lock acquired. Writing 4 images...")
                    
                    while image_to_mapping_queue.size() < 4:
                        pass
                    for i in range(4):
                        image_data = image_to_mapping_queue.get()
                        # img_path = os.path.join(SHARED_DIR, f"received_{image_data.device_id}.jpg")
                        # cv2.imwrite(img_path, image_data.image)

                        tmp_path = os.path.join(TEMP_DIR, f"received_{image_data.device_id}_temp.jpg")
                        cv2.imwrite(tmp_path, image_data.image) # This handles the JPEG formatting automatically!

                        # 2. Swap it
                        jpg_path = os.path.join(SHARED_DIR, f"received_{image_data.device_id}.jpg")
                        os.replace(tmp_path, jpg_path)
                            
                finally:
                    fcntl.flock(lock_file, fcntl.LOCK_UN)
                    print("🔓 Images written. Lock released.")

    finally:
        image_receiver_manager.stop_workers()
    return 0


if __name__ == "__main__":

    result_main = main()
    if result_main < 0:
        print(f"ERROR: Status code: {result_main}")

    print("Done!")
