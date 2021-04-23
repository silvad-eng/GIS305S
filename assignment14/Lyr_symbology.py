import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")
map_doc = aprx.listMaps()[0]

#Layers
lyr=map_doc.listLayers("U.S. States (Generalized)")[0]

#Get the existing symbol.
sym = lyr.symbology
sym.renderer.symbol.color = {'RGB': [255, 0, 0, 100]}
sym.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}
lyr.symbology = sym
lyr.transparency = 50