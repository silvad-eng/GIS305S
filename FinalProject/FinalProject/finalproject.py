import yaml
import logging
import arcpy
import csv

from etl.GSheetsEtl import GSheetsEtl

def setup():
    """
     Set up the configuration dictionary and the log file.

     parameters: Loads the yaml file
     returns: The configuration dictionary

    """
    with open('config_dict/wnvoutbreak.yaml') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

        logging.basicConfig(level=logging.DEBUG, filename= "wnvoutbreak.log", filemode="w", format='%(name)s - ''%(levelname)s - ''%(message)s')

    return config_dict


def etl():
    """
    The etl process will be initiated here. The data will be extracted from the google form, it
    will then be transformed into an XYTable(json file) that can be then be loaded into ArcGIS Pro
    for further calculations.

    parameter: configuration dictionary
    returns: avoid points layer

    """
    logging.debug("Etl process has begun, if error occurs go to GSheetsEtl.")
    print("Start etl process....")
    etl_instance = GSheetsEtl(config_dict)
    etl_instance.process()

def buffer(layer, dist):
    """
    buffer function: Will create 1500-foot buffer for 4 layers: OSMP, Lakes and Reservoirs, Mosquito Larval Sites
    and Wetlands. Produces a list of layers each with a 1500-foot buffer.

    parameters: layer list(layer), distance (dist)
    returns: nothing

    """
    units = " feet"
    distance = str(dist) + units

    # Output location path for the buffered layer
    output_layer = f"{layer}_buff"

    # Buffer analysis tool (input variable name, output variable name, distance type string,"FULL", "ROUND", "ALL")
    arcpy.Buffer_analysis(layer, output_layer, distance, "FULL", "ROUND", "ALL")
    print("Buffer created " + output_layer)
    return

def intersect(inter_list):
    """
    intersect function, will intersect all layers with 1500-foot buffer to find common areas
    includes the avoid points layer.

    parameter: list of layers with 1500-foot buffer
    return: The final path and name of the intersected layer, _allinter

    """
    logging.info("Intersecting all buffered layers.")
    # print the list being passed in
    print(inter_list)

    # ask the user to define an output intersect layer and store the results in a variable
    output_layer = f"{config_dict.get('proj_dir')}\WNVOutbreak.gdb\_allinter"

    # run a intersect analysis between the two buffer layer name and store the result in a variable
    # using arcpy.Intersect_analysis
    arcpy.Intersect_analysis(inter_list, output_layer)
    print("Intersect has been completed")
    return output_layer

def erase(erase_points):
    """
    erase function: erase all avoid points buffered layer from the intersect layer

    parameters: erase_points (avoid points layer with 1500-foot buffer)
    returns: out_feature_name (final path with final_analysis name)

    """
    logging.info("Erasing the avoid points areas for final layer output.")
    print("Erase layer is being created.")

    in_features = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\_allinter"
    # in_features = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spatial_join"
    avoidpoint = erase_points
    out_feature_name = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spj_werasedpoints_layer"
    arcpy.Erase_analysis(in_features, avoidpoint, out_feature_name)
    print("Avoid points layer has been erased, final analysis layer is ready.")
    return out_feature_name

def spatial(erase_layer):
    """
    spatial function: creates a spatial join layer with addresses and final analysis layer
    parameters: erase_layer (this is the final analysis layer)
    returns: spj_file (a spatial joined addresses will the final analysis layer)

    """
    logging.info("Spatial joining all the addresses and the final analysis layer.")
    print("Addresses and Final_Analysis layer are being joined")

    target_feature = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\Addresses"
    join_feature = erase_layer
    spj_file = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spatial_join"
    arcpy.SpatialJoin_analysis(target_feature, join_feature, spj_file)
    print("Spatial Join has been completed")
    return spj_file


def spatialreference(map_final):
    """
    spatialreference function: will set the map document to a spatial reference of 102653
    (NAD 1983 StatePlane Colorado North FIPS 0501Feet-Northern Colorado State Plane).
    parameters: map_final
    returns: map_final.spatialReference (a spatial referenced map)

    """
    logging.info("Spatial Reference for map document will be set to Northern Colorado State Plane")
    noco = 102653
    state_plane_noco = arcpy.SpatialReference(noco)
    map_final.spatialReference = state_plane_noco
    print("Spatial Reference set to 102653- North Colorado State Plane (feet).")
    return map_final.spatialReference

def exportMap(aprx):
    """
    exportMap function: Sets the spatial reference for the final map document, prints a list
    of the map layouts, prints a list the elements found on the map document and takes the
    Final_Analysis layer-applies a simple renderer (symbology red with transparency of 50% red.
    It then exports a pdf of the final map.
    parameters: aprx (current project)
    returns: a pdf map in the project directory of the yaml file.

    """
    logging.info("Exporting final map has begun.")
    map_final = aprx.listMaps()[0]

    # Setting spatial reference
    spatialreference(map_final)


    # List Map Layout in WNVOutbreak Project
    lyt_list = aprx.listLayouts()[0]
    print(lyt_list.name)

    # List elements within the map layout such as the title, the legend and etc..
    for el in lyt_list.listElements():
        print(el.name)
        if "Title" in el.name:
            el.text = el.text
        if "Date" in el.name:
            el.text = el.text

    # Layers: TargetAddresses
    lyr = map_final.listLayers("Final_Analysis")[0]

    # Get the existing symbol and sets the Final_Analysis layer to red.
    sym = lyr.symbology
    sym.renderer.symbol.color = {'RGB': [255, 0, 0, 100]}
    sym.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}
    lyr.symbology = sym
    lyr.transparency = 10

    # Save all the aprx to the
    aprx.save()

    # Export final map to a pdf using the user input name.
    lyt_list.exportToPDF(f"{config_dict.get('proj_dir')}\\final_map")
    return

# def exporttocsv(TargetAddresses_shape):
#     """
#       exportocsv function: Takes the final spatial join of the all addresses in the mosquito spraying zone
#       then takes the field full address in the table and exports every row in the table (should be around 9,038
#       this is based on a 1500-foot buffer applied to all layers).
#
#       parameters: TargetAddresses_shape
#       returns: .csv file will addresses to be contacted for mosquito spraying into the yaml project directory
#
#     """
#     logging.info("Exporting to CSV.")
#     print("Export addresses to csv table.")
#     fc = TargetAddresses_shape
#     fields = ["FULLADDRES"]
#     outCsv = f"{config_dict.get('proj_dir')}\WNVOutbreak.gdb\Target_Addresses"
#
#     with open(outCsv,'w') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow(fields)
#             with arcpy.da.SearchCursor(fc,fields) as cursor:
#                 for row in cursor:
#                     writer.writerow(row)
#             print(f"CSV is created, here is the path:{outCsv}")
#     csvfile.close()
#     return









def main():
    """
    main function: In the main function, all of the analysis will be taking place-by calling previous made functions
    and returning necessary layers for final map. The workspace is set by the yaml file: proj_dir. All processes are
    set to overwrite previously done processes (however at time this might become an issue and will require used to
    delete files manually(a flush function can be added to reduce this problem).

    Buffer, intersect, spatial join, clip, and counting functions will take place within this section.

    parameters: proj_dir (project directory found in the yaml file)
    return: pdf final map and csv table of full address to contact for mosquito spraying.

    """
    logging.info("WNVOutbreak start logging:...")
    arcpy.env.workspace = f"{config_dict.get('proj_dir')}\WNVOutbreak.gdb"

    # # Setting the extent of the environment using space-delimited string
    # arcpy.env.extent="-105.2705, 40.015, 0.5, 0.25"

    # Setting overwrite to true, this will allow for previously developed files to be overwritten by a new version.
    arcpy.env.overwriteOutput = True
    LayerList = ["Mosquito_Larval_Sites", "Wetlands_Regulatory", "OSMP_Properties", "Lakes_and_Reservoirs_Boulder_County", "avoid_points"]



    # Buffer all layers in the Layerlist to 1500 feet.
    for layer in LayerList:
        dist = 1500
        bufferlayer = buffer(layer,dist)


    # Intersect all buffered layers except avoid points layer (total of 4)
    logging.debug("Intersect...")
    inter_list = ['Mosquito_Larval_Sites_buff', 'Wetlands_Regulatory_buff', 'OSMP_Properties_buff', 'Lakes_and_Reservoirs_Boulder_County_buff']
    try:
        output_intersectlayer = intersect(inter_list)
        print(f"{output_intersectlayer}")
    except:
        print("Something went wrong with the intersect all buffered layers function.")


    #Intersect all buffered layers and the avoid points layer as well
    logging.debug("Intersect all buffered layers and the avoid points layer for final analysis layer.")
    inter_list2 =["_allinter", "avoid_points_buff"]
    outputlayer_avpt=f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\intersect_avpt"
    try:
        arcpy.Intersect_analysis(inter_list2, outputlayer_avpt)
        print("Intersect avoid points layer complete.")
    except:
        print("Something went wrong with the intersect between all buffered layers and"
              "the avoid points layers.")


    # Erase the avoid points buffer layer from the intersect layer, display final layer for areas
    # that will be sprayed for mosquitoes.
    logging.debug("Erase new address points from spatial join layer.")
    erase_points = "intersect_avpt"
    try:
        erase_layer = erase(erase_points)
        print(f"Erases new address file from spatial join: {erase_layer}")
    except:
        print("Something went wrong with the Erase the avoid points layer from "
              "the intersect layer.")


    # Spatial Join of all the buffered layers.
    logging.debug("Spatial Join all the buffered layers.")
    try:
        finaloutput_spjlayer = spatial(erase_layer)
        print(f"New Spatial Join Layer named: {finaloutput_spjlayer}")
    except:
        print("Something went wrong with the spatial join for all the buffered layers"
              "and addresses.")


    # Clip Addresses to final analysis layer.
    try:
        logging.debug("Clip addresses to final analysis layer to get target addresses to contact for spraying.")
        TargetAddresses = arcpy.Clip_analysis("Addresses",erase_layer,"Target_Addresses")
        print(f"Final target address layer has been completed:{TargetAddresses}")

        # Count the number of addresses to be contacted.
        logging.debug("GetCount for target address file.")
        address_count = arcpy.management.GetCount(TargetAddresses)
        print(f"Number of addresses to be contacted for mosquito spraying:{address_count}")

        # Convert Target Addresses feature class to a shapefile
        logging.debug("Convert feature layer to a shapefile.")
        TargetAddresses_shape = arcpy.conversion.FeatureClassToShapefile(TargetAddresses,
                                                                         f"{config_dict.get('proj_dir')}\\TargetAddresses_shape")
        print(f"Target Address layer has been converted to a shapefile: {TargetAddresses_shape}")
    except:
        print("Something went wrong with the clipping addresses to final analysis layer.")




    # # Export addresses to csv
    # exporttocsv(TargetAddresses_shape)
    # print("CSV done.")




    # Get Project, set layout, save project and look at map in ArcGIS pro. Export csv file with target addresses.
    logging.info("Creating the layout and saving final map to a pdf.")
    aprx = arcpy.mp.ArcGISProject(f"{config_dict.get('proj_dir')}WNVOutbreak.aprx")
    map = exportMap(aprx)
    # csvlist=exporttocsv()

    print("Final Map Done! Check the file folder for output map and csv.")



if __name__ == '__main__':
    global config_dict
    config_dict = setup()
    print(config_dict)
    etl()
    main()



