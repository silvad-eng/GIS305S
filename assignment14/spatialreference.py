import arcpy

#Get the list of spatial references
srs = arcpy.ListSpatialReferences("*utm/north america*")

#create a spatialreference object for each one and print the central meridian
for sr_string in srs:
    sr_object = arcpy.SpatialReference(sr_string)
    print("{0.centralMeridian} {0.name} {0.PCSCode}".format(sr_object))

aprx = arcpy.mp.ArcGISProject(r"E:\GIS\GIS305\Data\Lesson1\Lesson1Exercise\Lesson1.aprx")
map_doc = aprx.listMaps()[0]

#https://www.spatialreference.org/ref/esri/3743/UTM13
state_plane_noco = arcpy.SpatialReference(3743)
map_doc.spatialReference = state_plane_noco