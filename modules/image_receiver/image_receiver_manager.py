"""
Collect and enqueue images from multiple network connections. 
"""

from collections import deque
import logging
import multiprocessing as mp

from utilities.message_queue import MessageQueue
from .image_receiver_worker import ImageReceiverWorker


class ImageReceiverManager:
    """
    Receives and aggregates images from multiple network connections.
    """

    __WORKER_JOIN_TIMEOUT_SECONDS = 10.0
    __logger = logging.getLogger(__name__)

    def __init__(
        self,
        base_port: int,
        number_of_connections: int,
        image_queue: MessageQueue,
    ) -> None:
        """
        Class constructor.

        Parameters
        ----------
        base_port: The base port for TCP network connections.
        number_of_connections: The number of connections.
        image_queue: A queue used to send image data.
        """
        self.__base_port = base_port
        self.__number_of_connections = number_of_connections
        self.__image_queue = image_queue

        self.__workers = deque()
        self.__stop_event = mp.Event()

    def start_workers(self) -> None:
        """
        Start image receiver workers.
        """
        for id in range(self.__number_of_connections):
            port = self.__base_port + id
            self.__logger.info(f"Spawning worker for network port {port}")

            image_receiver_worker = ImageReceiverWorker(
                port=port,
                stop_event=self.__stop_event,
                image_queue=self.__image_queue,
            )

            process = mp.Process(target=image_receiver_worker.run, name=f"Worker-{id}")
            process.start()

            self.__logger.info(f"Process {process.name} (PID {process.pid}) spawned listening at port {port}")

            self.__workers.append(process)

    def stop_workers(self) -> None:
        """
        Stop image receiver workers.
        """
        self.__stop_event.set()

        for process in self.__workers:
            self.__logger.info(f"Joining process {process.name} (PID {process.pid})")
            process.join(self.__WORKER_JOIN_TIMEOUT_SECONDS)

        while self.__workers:
            process = self.__workers.popleft()

            if process.is_alive():
                self.__logger.warning(f"Terminating process {process.name} (PID {process.pid})")
                process.terminate()
