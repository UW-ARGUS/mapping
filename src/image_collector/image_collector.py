"""
Collect and enqueue images from multiple network connections. 
"""

class ImageCollector:
    """
    Receives and aggregates images from multiple network connections.
    """

    def __init__(
        self,
        base_port: int,
        connection_count: int,
    ) -> None:
        """
        Class constructor.

        Parameters
        ----------
        base_port: The base port for TCP network connections.
        connection_count: The number of connections.
        """
        self.__base_port = base_port
        self.__connection_count = connection_count
