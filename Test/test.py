import sys, os
sys.path.insert(0, os.path.abspath(os.path.join('..', 'docs/source')))
import fdtdgeometrywriter as writer
import matplotlib.pyplot as plt
params = writer.getParams("io/pphinfoini.json", "io/params.json")
writer.writeGeometry("io/geometry.json",params)
writer.PreviewLayerPlacement(params)