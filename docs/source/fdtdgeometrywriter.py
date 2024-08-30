from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

class GeometryEntry():
    """GeometryEntry() Class that holds information needed to write to a geometry.json file.

    An entry to the geometry.json file requires the following information

        Position  -> Position of Center Point

        Length    -> Geometry Size in Z-axis

        Width     -> Geometry Size in X-axis

        Thickness -> Geometry Size in Y-axis

        Material  -> Material of Geometry 

        Shape     -> Geometry Shape

        Radius    -> Corner Radius of the Geometry Shape

    This class holds this information about each geometry entry to later be written into 
    the geometry.json file
    """
    def __init__(self, Boundaries, Width, Material, Thickness):
        self.Boundaries = Boundaries
        self.Position = midpoint(Boundaries[0], Boundaries[1])
        self.Length = 1
        self.Width = Width
        self.Thickness = Thickness
        self.Material = Material
        self.Shape = "Rectangle"
        self.Radius = 1

def midpoint(p0, p1):
    return (int((p0[0] + p1[0])/2), int((p0[1] + p1[1])/2))

def rgba2state(pixels):
    """rgba2state() Convert rgba values to a state vector.

    if an rgb value for an input pixel is anything other than (255, 255, 255) then the state is 1
    otherwise the state is 0.

    Args:
        pixels: a list of three pixel arrays corresponding to the previous, current, and next pixel

    Returns:
        a 3-bit binary number represented as a vector denoting a state that Image2GeometryEntryList()
        recognizes.


    """
    state = [0, 0, 0]
    for i in range(len(pixels)):
        R,G,B,_ = pixels[i]
        if R != 255 or G != 255 or B != 255:
            state[i] = 1
    return state


def Image2GeometryEntryList(img, material, thickness):
    """Image2GeometryEntryList() function to convert image file to a list of GeometryEntry objects.

        This is the main algorithm for this program, and how it works is detailed in the Tutorial
        page but in general the process that is followed is for every pixel of the input image a
        state vector is found by checking the value of the previous pixel, current pixel, and next
        pixel where a white pixel is represented by 0 and a colored pixel is represented by 1. This
        state vector has four useful states, [0, 1, 0] denoting a single pixel entry, [0, 1, 1]
        denoting the beginning of a new entry, [1, 1, 1] denoting that a block should be added the 
        current entry, and [1, 1, 0] denoting that the current block is the last block in the entry.
        for each entry a GeometryEntry object is created and appended to a material list which is then
        returned at the end.

        Args:
            img: png File Imported by the Python Image Library
            material: name of the material corresponding to a index of refraction in the 3D-FDTD code
            thickness: size of the material layer in the Y-axis, reported in number of pixels

        Returns:
            A list of GeometryEntry objects corresponding to each line of material detected in the 
            image file

    """
    A = np.asarray(img)
    y,x,_ = A.shape
    B0 = []; B1 = []; width = 0
    MaterialList = []
    for row in range(len(A[:,0])):
        #for now the first and last column of the image are not allowed
        #to have information written to them so we don't include them in the loop
        for col in range(1, x-1):
            #the state reflects the material value at the previous, current
            #and next pixel stated as a 3-bit binary number
            state = rgba2state([A[row,col-1], A[row,col], A[row,col+1]])
            if state == [0, 1, 0]:
                #if the state is only 1 in the center digit there is only a
                #single block of material so it can be written directly to
                #the material list
                temp = GeometryEntry(Boundaries = [(col, row), (col, row)],
                    Width = 1,Material = material,Thickness = thickness)
                MaterialList.append(temp)
            elif state == [0,1,1]:
                #if only the first digit of the state is a zero then this
                #is the first block of material in a run so we can state this
                #as the left boundary coordinate and initialize the width counter
                B0 = (col, row)
                width = 1
            elif state == [1,1,1]:
                #if all digits of the state are one then we should have already started
                #a new block and now we just need to add one to the width counter
                width += 1
            elif state == [1,1,0]:
                #if only the last digit of the state is zero then we are in the last
                #block of material which is the right boundary so we add the last pixel
                #to the width counter and write the material information to the Material List
                width += 1
                B1 = (col, row)
                temp = GeometryEntry(Boundaries = [B0, B1],
                    Width = width,Material = material,Thickness = thickness)
                MaterialList.append(temp)
                width = 0
    return MaterialList

