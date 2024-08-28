from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def getPixelMaterial(px):
    """Retrieve the Material of the Current Pixel.
    
    Take in a pixel of the material image and determine based on the
    RGB value if this pixel is the current material or the background
    material. White Pixels correspond to background material and Black
    pixels correspond to Current Material pixels with in-between colors
    are returned as 0.5 which is presently unused in the writer algorithm
    
    Args:
        px: Current Pixel of Geometry Image File (Array) 

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

def midpoint(p0, p1):
  return (int((p0[0] + p1[0])/2), int((p0[1] + p1[1])/2))

class MaterialBlock():
  """Class to Hold Material Block Data.

  A material block refers to an individual entry to the geometry.json
  file this class contains all of the relevant information for an entry
  to the geometry.json file including the following

    Position  -> Midpoint of the material block, determined from Boundaries

    Length    -> How long is the Material in the Current Layer, Always 1

    Width     -> Number of Pixels in the material block

    Thickness -> How thick the material layer is along the Propogation Axis

    Material  -> Material Name for the material layer

    Shape     -> Always "Rectangle"

    Radius    -> How Rounded are the Corners, Always 1

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

def getMaterialList(image, Material, Thickness):
    """Create a List of Current Material Geometry Information.

    Args:
        image: material layer image
        Material: material layer name
        Thickness: thickness of curren material layer

    Returns:
        List of Material Block Objects

    """
    a = np.asarray(im)
    Y = a.shape[0]
    X = a.shape[1]
    count = 0
    StartBound = []
    MaterialList = []
    EndBound = []
    nBlocks = 0
    for row in range(Y):
        count = 0
        for col in range(X):
            if col == 0:
                px1 = getPixelMaterial(a[row, col, :])
                px2 = getPixelMaterial(a[row, col+1, :])
                px0 = px1
            elif col == X-1:
                px0 = getPixelMaterial(a[row, col-1, :])
                px1 = getPixelMaterial(a[row, col, :])
                px2 = px1
            else:
                px0 = getPixelMaterial(a[row, col-1, :])
                px1 = getPixelMaterial(a[row, col, :])
                px2 = getPixelMaterial(a[row, col+1, :])

            if px1 == 1 and px0 == 0:
                count = 1
                StartBound = (col, row)
                nBlocks += 1

            if px1 ==1 and px2 == 1:
                count += 1

            if px1 == 1 and px2 == 0:
                MatL.append(count)
                MaterialBlock
                EndBound = (col, row)
                Bounds = [StartBound, EndBound]
                temp = MaterialBlock(Boundaries = Bounds,
                                        Width = count,
                                        Material = Material,
                                        Thickness = Thickness)
                MaterialList.append(temp)
                count = 0
    print(f"{nBlocks} Detected")
    return MaterialList

def DisplayPreview(MaterialList, DomainSize):
    """Plot a Preview of the MaterialBlocks.
    """
    fig_width = DomainSize[2]
    fig_length = DomainSize[0]
    scale = fig_length / fig_width
    fig= plt.figure(figsize=(5,int(5*scale)))
    for i in range(len(MaterialList)):
        x, y = MaterialList[i].Position
        xmin, ymin = MaterialList[i].Boundaries[0]
        xmax, ymax = MaterialList[i].Boundaries[1]
        plt.plot([xmin,xmax], [ymin,ymax], color = 'black')
        plt.xlim(0,DomainSize[2])
        plt.ylim(0,DomainSize[0])
        plt.title("XZ Preview")
    return plt.show()

def GeometryEntryString(M, stepsize, layer):
    """Create a String for the geometry.json file entry.
    """
    x, z = M.Position
    y = layer
    l1 = f'"shape": "{M.Shape}",'
    l2 = f'"radius": {M.Radius}e-9,'
    l3 = f'"length": {M.Length}e-9,'
    l4 = f'"width": {M.Width}e-9,'
    l5 = f'"thickness": {M.Thickness}e-9,'
    l6 = f'"material": "{M.Material}",'
    l7 = f'"position": [{x},{y},{z}]'
    return "{" + l1 + l2 + l3 + l4 + l5 + l6 + l7 + "}"

def WriteGeometry(MaterialList, StepSize, Layer):
    """Write Each Geometry Entry String to geometry.json file.
    """
    f = open("geometry.json", "a")
    for i in range(len(MaterialList)-2):
        f.write(GeometryEntryString(MaterialList[i], StepSize, Layer) + ",")
    f.write(GeometryEntryString(MaterialList[-1], StepSize, Layer) + ",")


def MaterialLayerPreview(MaterialLayer, MaterialThickness, DomainSize):
    """Plot a Preview of the Material Layer Placement.
    """
    fig, ax = plt.subplots()
    fig_width = DomainSize[2]
    fig_length = DomainSize[1]
    scale = fig_length / fig_width
    fig.set_figheight(5*scale)
    fig.set_figwidth(5)
    plt.ylim(0,DomainSize[1])
    plt.xlim(0,DomainSize[2])
    for i in range(len(MaterialLayer)):
        coord = [[DomainSize[2]/2+DomainSize[2],MaterialLayer[i]+MaterialThickness[i]/2],
            [DomainSize[2]/2+DomainSize[2], MaterialLayer[i]-MaterialThickness[i]/2],
            [DomainSize[2]/2-DomainSize[2], MaterialLayer[i]-MaterialThickness[i]/2],
            [DomainSize[2]/2-DomainSize[2], MaterialLayer[i]+MaterialThickness[i]/2]]
        if i == 0:
            p = Polygon(coord, facecolor = 'lightblue')
        elif i == 1:
            p = Polygon(coord, facecolor = 'gray')
        else:
            p = Polygon(coord, facecolor = 'gold')
        ax.add_patch(p)
    plt.title("Material Layer Preview")
    plt.show()