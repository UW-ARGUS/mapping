"""
ARGUS 3D mapping reconstruction.
"""

import time
import multiprocessing as mp

from modules.image_collector.image_receiver_controller import ImageReceiverController 


def main() -> int:
    """
    Main function.
    """ 
    # TODO: These values should come from a config file
    base_port = 5000
    number_of_connections = 1
    image_to_mapping_queue = mp.Queue()

    image_receiver_controller = ImageReceiverController(
        base_port=base_port,
        number_of_connections=number_of_connections,
        image_queue=image_to_mapping_queue,
    )

    try:
        image_receiver_controller.start_workers()
        time.sleep(20)
    finally:
        image_receiver_controller.stop_workers()

    return 0


if __name__ == "__main__":
    result_main = main()
    if result_main < 0:
        print(f"ERROR: Status code: {result_main}")

    print("Done!")
