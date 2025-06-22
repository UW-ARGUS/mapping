"""
ARGUS 3D mapping reconstruction.
"""

import cv2
import time
import multiprocessing as mp

from modules.image_data import ImageData
from modules.image_collector.image_receiver_controller import ImageReceiverController 


def main() -> int:
    """
    Main function.
    """ 
    # TODO: These values should come from a config file
    base_port = 5000
    number_of_connections = 4
    image_to_mapping_queue = mp.Queue()

    image_receiver_controller = ImageReceiverController(
        base_port=base_port,
        number_of_connections=number_of_connections,
        image_queue=image_to_mapping_queue,
    )

    try:
        image_receiver_controller.start_workers()

        while True:
            image_data = image_to_mapping_queue.get()

            if image_data is None:
                continue

            assert isinstance(image_data, ImageData)

            cv2.putText(
                image_data.image,
                f"{image_data.timestamp:.3f}",
                (10, 20),  # Top-left corner
                cv2.FONT_HERSHEY_SIMPLEX,  # Font type
                0.5,  # Font size
                (255, 0, 255),  # Fuschia
                1,  # Line thickness
            )

            cv2.imshow(f"Image display", image_data.image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if cv2.getWindowProperty("Image display", cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        image_receiver_controller.stop_workers()

    return 0


if __name__ == "__main__":
    result_main = main()
    if result_main < 0:
        print(f"ERROR: Status code: {result_main}")

    print("Done!")
