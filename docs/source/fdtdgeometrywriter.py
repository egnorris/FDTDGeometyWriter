from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def getPixelColor(px):
    """
    Get the RGBA values for a given pixel in the geometry image
    
    Args:
        px (array): Current Geometry Image Pixel

    Returns:
        R    (int): Value of Red Color Channel
        G    (int): Value of Green Color Channel
        B    (int): Value of Blue Color Channel
        A  (float): Value of Alpha Channel
    """
    R = px[0]
    G = px[1]
    B = px[2]
    A = px[3]
    return R, G, B, A