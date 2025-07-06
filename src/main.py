"""
ARGUS 3D mapping reconstruction.
"""

import cv2

from modules.image_data import ImageData
from modules.image_receiver.image_receiver_manager import ImageReceiverManager
from utilities.message_queue import MessageQueue


def main() -> int:
    """
    Main function.
    """
    # TODO: These values should come from a config file
    base_port = 5000
    number_of_connections = 2
    image_state_array = []
    image_data_array = []
    image_to_mapping_queue = MessageQueue[ImageData](maxsize=100)

    for _ in range(number_of_connections):
        image_data_array.append(None)
        image_state_array.append(False)

    image_receiver_manager = ImageReceiverManager(
        base_port=base_port,
        number_of_connections=number_of_connections,
        image_queue=image_to_mapping_queue,
    )

    image_receiver_manager.start_workers()

    while True:
        try:
            image_data = image_to_mapping_queue.get()

            if image_data is None:
                continue

            # Update the state array with image device id
            image_state_array[image_data.device_id] = True

            # Check if 3D reconstruction pipeline should run
            if all(image_state_array):
                assert all(image_data is not None in image_data_array)

                # Run VGGT
                pass

        except KeyboardInterrupt as e:
            image_receiver_manager.stop_workers()
            break

    return 0


if __name__ == "__main__":
    result_main = main()
    if result_main < 0:
        print(f"ERROR: Status code: {result_main}")

    print("Done!")
