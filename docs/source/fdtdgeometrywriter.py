"""Writes geometry.json for input image
Description
-----------

Author(s)
---------
- Created by Evan Norris 08/28/2024.
Members
-------
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def getPixelMaterial(px):
    """GetPixelMaterial() retrieve the Material of the Current Pixel.
    
    Take in a pixel of the material image and determine based on the
    RGB value if this pixel is the current material or the background
    material. White Pixels correspond to background material and Black
    pixels correspond to Current Material pixels with in-between colors

    are returned as 0.5 which is presently unused in the writer algorithm
    
    Args:
        px: (Array) Current Pixel of Geometry Image File

    Returns:
        Material State - Either 0 for vacuum, 1 for current material, or 0.5 otherwise

    """
    R,G,B,_ = px
    if R == 255 and G == 255 and B == 255:
        return 0
    elif R == 0 and G == 0 and B == 0:
        return 1
    else:
        return 0.5

