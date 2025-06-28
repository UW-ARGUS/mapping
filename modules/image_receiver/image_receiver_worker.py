"""
A worker class to receive image data from a network connection.
"""

import logging
import multiprocessing as mp
import socket
import struct

import cv2
import numpy as np

from utilities.message_queue import MessageQueue
from modules.image_data import ImageData


class ImageReceiverWorker:
    """
    Accepts TCP connection and receives images over network.
    """

    __HOST_IP_ADDRESS = "0.0.0.0"
    __IMAGE_HEADER_LENGTH_BYTES = 16
    __SOCKET_TIMEOUT_SECONDS = 10.0
    __logger = logging.getLogger(__name__)

    def __init__(
        self,
        port: int,
        stop_event: mp.Event,
        image_queue: MessageQueue,
    ) -> None:
        """
        Class constructor.

        Parameters
        ----------
        port: The port to receive image data from.
        stop_event: An event to signal the worker to halt.
        image_queue: A queue used to send image data.
        """
        self.__port = port
        self.__stop_event = stop_event
        self.__image_queue = image_queue

        self.__connection = None

    def __del__(self) -> None:
        """
        Class destructor.
        """
        if self.__connection is not None:
            self.__connection.close()

    def run(self) -> None:
        """
        Receives images from a TCP connection and enqueues the data.

        Note: This method will be the task the worker performs.
        """
        try:
            connection_successful = self.__setup_socket()

            while not self.__stop_event.is_set() and not connection_successful:
                self.__logger.info("Retrying connection")
                connection_successful = self.__setup_socket()

            while not self.__stop_event.is_set():
                try:
                    image_data = self.__receive_image_data()
                except socket.timeout:
                    self.__logger.exception("Connection timed out")
                    continue 

                self.__image_queue.put(image_data)
        finally:
            self.__image_queue.flush_and_drain_queue()
            return

    def __receive_image_data(self) -> ImageData:
        """
        Receive image from network.

        Returns
        -------
        ImageData: Image data received from network.
        """
        # Receive image header from network
        raw_image_header = b""
        while len(raw_image_header) < self.__IMAGE_HEADER_LENGTH_BYTES:
            packet = self.__connection.recv(self.__IMAGE_HEADER_LENGTH_BYTES - len(raw_image_header))

            if not packet:
                self.__logger.warning("Invalid image header data")
                continue

            raw_image_header += packet

        timestamp, device_id, image_data_length = struct.unpack(
            ">dII",  # Big endian (network endiannes), float64, uint32, uint32
            raw_image_header,
        )

        # Receive image data from network
        raw_image_data = b""
        while len(raw_image_data) < image_data_length:
            packet = self.__connection.recv(image_data_length - len(raw_image_data))

            if not packet:
                self.__logger.warning("Invalid image data")
                continue

            raw_image_data += packet

        image_array = np.frombuffer(raw_image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        return ImageData(
            timestamp,
            device_id,
            image_data_length,
            image,
        )

    def __setup_socket(self) -> bool:
        """
        Accept incoming TCP connection at network port.

        Returns
        -------
        bool: Indicates if the connection is accepted.
        """
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.settimeout(self.__SOCKET_TIMEOUT_SECONDS)
        socket_instance.bind((self.__HOST_IP_ADDRESS, self.__port))

        try:
            socket_instance.listen()
            self.__logger.info(f"Listening on {self.__HOST_IP_ADDRESS}:{self.__port}")

            connection, address = socket_instance.accept()
        except socket.timeout:
            self.__logger.exception("Connection timed out")
            socket_instance.close()
            return False

        self.__logger.info(f"Connected by address {address}")
        self.__connection = connection

        return True
