# Tutorial

## Required Input Files

### Testing Image
Below is the Input Image from the Included Testing Program of a material profile with a domain size of 500x500 pixels and a nanoantenna with two legs each with a width of 80 pixels and one 170 pixel leg and one 160 pixel leg. 

![image](../../Test/io/170x160-1cell.png)

### pphinfoini.json
```
   {
      "Domain Size": [500, 300, 500],
      "Domain Decomposition": [4, 4, 4],
      "Step Size": [1e-9, 1e-9, 1e-9],
      "PML Box": [20, 20, 20],
      "TFSF Box": [20, 20, 20],
      "Scattering Box": [10, 10, 10],
      "Total Box": [30, 30, 30],
      "Number of Time Steps": 10000,
      "Number of Wavelengths": 50,
      "Minimum Wavelength": 500e-09,
      "Maximum Wavelength": 1500e-09,
      "ANTENNA_TYPE": 1000,
      "Center Position": [250, 150, 250]
   }
```

### params.json
```
   {
      "MaterialLayer":[164, 151.5],
      "MaterialThickness":[25, 3],
      "MaterialLabel":["Gold", "Chromium"],
      "MaterialImagePath":["io/TestShape.png", "io/TestShape.png", "io/TestShape.png"]
   }
```
## Material Detection Algorithm

The primary mechanism of this program lies in the getMaterialList() subroutine which analyzes the input image and 
converts from a raster image to a list of materials to be written to a geometry.json file. Rather than writing each
image pixel to an entry in the geometry.json this code converts lines of pixels into a single geometry entry. 
### getMaterialList()
```{eval-rst}
.. automodule:: fdtdgeometrywriter.getMaterialList()
   :members:
```
### Writer State
The analysis scans every pixel and retreives a 3-bit binary string that is used as the "state" of the writer this
this string is built from the pixel at the previous index, the current pixel, and the pixel at the next index. There
are four such states detailed in the below image.

![image](images/geometry_writer_state_diagram.png)