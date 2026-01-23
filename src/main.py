"""
ARGUS 3D mapping reconstruction.
"""

import cv2
import numpy as np

from modules.image_data import ImageData
from modules.image_receiver.image_receiver_manager import ImageReceiverManager
from utilities.message_queue import MessageQueue


# Grid configuration
GRID_ROWS = 2
GRID_COLS = 2
TARGET_WIDTH = 640
TARGET_HEIGHT = 480


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

    # Store latest frame per device
    latest_frames: dict[int, ImageData] = {}

    try:
        image_receiver_manager.start_workers()

        while True:
            image_data = image_to_mapping_queue.get()

            if image_data is None:
                continue

            # Overlay timestamp
            cv2.putText(
                image_data.image,
                f"{image_data.timestamp:.3f}",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 255),
                1,
            )

            # Save latest frame for this device
            latest_frames[image_data.device_id] = image_data

            # Only render when all devices have sent at least one frame
            if len(latest_frames) == number_of_connections:
                frames = []

                for device_id in sorted(latest_frames.keys()):
                    frame = latest_frames[device_id].image
                    frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
                    frames.append(frame)

                # Build 2x2 grid
                top_row = np.hstack(frames[0:2])
                bottom_row = np.hstack(frames[2:4])
                grid = np.vstack((top_row, bottom_row))

                cv2.imshow("ARGUS Multi-Camera View", grid)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        image_receiver_manager.stop_workers()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    result_main = main()
    if result_main < 0:
        print(f"ERROR: Status code: {result_main}")

    print("Done!")
