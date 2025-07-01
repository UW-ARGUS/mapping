"""
A queue for sending and receiving inter-process messages.
"""

import multiprocessing as mp
import queue
import time
import typing


T = typing.TypeVar("T")


class MessageQueue(typing.Generic[T]):
    """
    Wrapper to multiprocessing queues.
    """

    __QUEUE_TIMEOUT_SECONDS = 0.1
    __QUEUE_DELAY_SECONDS = 0.1

    def __init__(
        self,
        maxsize: int = 0,
    ):
        """
        Class constructor.

        Parameters
        ----------
        maxsize: The maximum size of the queue.
        """
        self.__queue = mp.Queue(maxsize=maxsize)
        self.__maxsize = maxsize

    def put(self, message: T) -> None:
        """
        Puts a message in the queue.

        Parameters
        ----------
        message: The message to be placed in the queue.
        """
        try:
            self.__queue.put(message, timeout=self.__QUEUE_TIMEOUT_SECONDS)
        except queue.Full:
            return

    def get(self) -> None | T:
        """
        Gets a message in the queue.

        Returns
        -------
        T: The received message.
        """
        try:
            return self.__queue.get(timeout=self.__QUEUE_TIMEOUT_SECONDS)
        except queue.Empty:
            return None

    def flush_queue(self) -> None:
        """
        Flush the queue with `None` values.
        """
        try:
            for _ in range(self.__maxsize):
                self.__queue.put(None, timeout=self.__QUEUE_TIMEOUT_SECONDS)
        except queue.Full:
            return

    def drain_queue(self) -> None:
        """
        Drains the queue.
        """
        try:
            for _ in range(self.__maxsize):
                self.__queue.get(timeout=self.__QUEUE_TIMEOUT_SECONDS)
        except queue.Empty:
            return

    def flush_and_drain_queue(self) -> None:
        """
        Flush and drain the queue.
        """
        self.flush_queue()
        time.sleep(self.__QUEUE_DELAY_SECONDS)
        self.drain_queue()
