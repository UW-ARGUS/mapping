"""
Data class for images.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class ImageData:
    """
    Image data and timestamp.
    """

    timestamp: float
    data_length: int
    image: np.array
