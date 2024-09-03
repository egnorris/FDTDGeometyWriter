from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib as mpl
import json
import math

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
            material: name of the material corresponding to the index of refraction in the 3D-FDTD code
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


def SetupColor(colormap = 'tab20', nlines = 20):
    n_lines = nlines
    cmap = mpl.colormaps[colormap]
    return cmap(np.linspace(0, 1, n_lines))
    
def PreviewLayerPlacement(params):
    """PreviewLayerPlacement() Display visulization of Material Layer Placement in Y-X Plane.

    Args:
        LayerList: A list of layer placement for each to be written to the geometry.json file
        ThicknessList: A list of material size in the Y Axis for each material to to be written
                to the geometry.json file
        LabelList: A list of materials corresponding to the index of refraction in the 3D-FDTD code
            for each material to to be written to the geometry.json file
        Domain: Size of the 3D FDTD simulation domain

    Returns:
        pyplot figure
    """

    print("Warning: This only uses Material Thickness and Placement Data, the x-axis data is not based on Geometry Size")

    Domain = params["DomainSize"]
    LayerList = params["MaterialLayer"]
    ThicknessList = params["MaterialThickness"]
    LabelList = params["MaterialLabel"]
    fig, ax = plt.subplots()
    fig_width = Domain[2]
    fig_length = Domain[1]
    scale = fig_length / fig_width
    fig.set_figheight(10*scale)
    fig.set_figwidth(10)
    plt.ylim(0,Domain[1])
    plt.xlim(0,Domain[2])
    colors = SetupColor()

    coord = [[0,0], [0,Domain[1]], [Domain[2],Domain[1]], [Domain[2],0]]
    p = Polygon(coord, facecolor = 'white', label="Vacuum")
    ax.add_patch(p)

    for i in range(len(LayerList)):
        coord = [[Domain[2]/2+Domain[2],LayerList[i]+ThicknessList[i]/2],
            [Domain[2]/2+Domain[2], LayerList[i]-ThicknessList[i]/2],
            [Domain[2]/2-Domain[2], LayerList[i]-ThicknessList[i]/2],
            [Domain[2]/2-Domain[2], LayerList[i]+ThicknessList[i]/2]]
        p = Polygon(coord, facecolor = colors[i,:], label = LabelList[i])
        ax.add_patch(p)
    #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend()
    plt.title("Material Layer Preview")
    plt.savefig("GeometryLayerPreview.png")
    plt.show()

def getEntry(G, MaterialLayer, StepSize):
    """getEntry() convert a GeometryEntry object to a dictionary for geometry.json entry.

    Args:
        G: Geometry Entry Object
        MaterialLayer: Y-axis position of Geometry Entry Object in the 3D-FDTD Simulation
        StepSize: 3 Element vector of step sizes retrieved from pphinfoini.json

    Returns:
        a dictionary for geometry.json entry

    """
    StepSizeXMagnitude = 10**(math.floor(math.log(StepSize[0], 10)))
    StepSizeYMagnitude = 10**(math.floor(math.log(StepSize[0], 10)))
    StepSizeZMagnitude = 10**(math.floor(math.log(StepSize[0], 10)))
    StepSizeXMultiple = int(StepSize[0] / StepSizeXMagnitude)
    StepSizeYMultiple = int(StepSize[1] / StepSizeYMagnitude)
    StepSizeZMultiple = int(StepSize[2] / StepSizeZMagnitude)
    return {
            "shape": f"{G.Shape}",
            "radius": f"{G.Radius}{str(StepSizeXMagnitude)[1:]}",
            "length": f"{G.Length * StepSizeXMultiple}{str(StepSizeXMagnitude)[1:]}",
            "width": f"{G.Width * StepSizeZMultiple}{str(StepSizeZMagnitude)[1:]}",
            "thickness": f"{int(G.Thickness * StepSizeYMultiple)}{str(StepSizeYMagnitude)[1:]}",
            "material": f"{G.Material}",
            "position": [G.Position[0],MaterialLayer,G.Position[1]]}

def getParams(pphinfoFilePath, paramsFilePath):
    """getParams() open input files and convert them to a single params dictionary.

    Args:
        pphinfoFilePath: pphinfoini.json file path
        paramsFilePath: params.json file path

    Returns:
        A single parameters dictionary

    """
    f = open(paramsFilePath)
    params = json.load(f)
    f.close()
    MaterialLayer = params['MaterialLayer']
    MaterialThickness = params['MaterialThickness']
    MaterialLabel = params['MaterialLabel']
    MaterialImagePath = params['MaterialImagePath']
    MaterialImages = []
    for i in range(len(MaterialLabel)):
        if i >= len(MaterialImagePath):
            #if more materials are being used than image paths then use the last defined image
            #path for all remaining shapes
            MaterialImages.append(Image.open(MaterialImagePath[len(MaterialImagePath)-1]))
        else:
            MaterialImages.append(Image.open(MaterialImagePath[i]))
    f = open(pphinfoFilePath)
    params = json.load(f)
    f.close()
    DomainSize = params["Domain Size"]
    StepSize = params["Step Size"]
    CenterPosition = params["Center Position"]
    return {
        "MaterialLayer": MaterialLayer,
        "MaterialThickness": MaterialThickness,
        "MaterialLabel": MaterialLabel,
        "MaterialImages": MaterialImages,
        "DomainSize": DomainSize,
        "StepSize": StepSize,
        "CenterPosition": CenterPosition}

def writeGeometry(filepath,params):
    """writeGeometry() Write Geometry Entry Objects to a geometry.json file

    Args:
        filepath: path where geometry.json will be saved
        params: paramter dictionary constructed from pphinfoini.json and params.json

    Returns:
        A single parameters dictionary

    """
    MaterialLayer = params["MaterialLayer"]
    MaterialThickness = params["MaterialThickness"]
    MaterialLabel = params["MaterialLabel"]
    MaterialImages = params["MaterialImages"]
    StepSize = params["StepSize"]
    while True:
        try:
            f = open(filepath, "x")
            f.close()
            break
        except FileExistsError:
            f = open(filepath, "w")
            f.close()
            break
    f = open(filepath, "w")
    f.write("[")
    for i in range(len(MaterialLabel)):
        G = Image2GeometryEntryList(MaterialImages[i], MaterialLabel[i], MaterialThickness[i])
        for k in range(len(G)-2):
            Entry = getEntry(G[k], MaterialLayer[i], StepSize)
            json.dump(Entry, f)
            f.write(",")
        Entry = getEntry(G[k], MaterialLayer[i], StepSize)
        json.dump(Entry, f)
        if i <= len(MaterialLabel)-2:
            f.write(",")
    f.write("]")
