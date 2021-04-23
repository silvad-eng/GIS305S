import arcpy

aprx = arcpy.mp.ArcGISProject(r"E:\GIS\GIS305\Data\Lesson1\Lesson1Exercise\Lesson1.aprx")
map_doc = aprx.listMaps()[0]

lyr = map_doc.listLayers("U.S. States (Generalized)")[0]

lyr.definitionQuery = "STATE_NAME='Colorado'"