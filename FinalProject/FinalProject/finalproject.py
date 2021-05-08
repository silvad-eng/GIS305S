import yaml
import logging
import arcpy

from etl.GSheetsEtl import GSheetsEtl

def setup():
    """
     Set up the configuration directory and the log file.
    """
    with open('config_dict/wnvoutbreak.yaml') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

        logging.basicConfig(level=logging.DEBUG, filename= "wnvoutbreak.log", filemode="w", format='%(name)s - ''%(levelname)s - ''%(message)s')

    return config_dict


def etl():
    """
    The etl will be
    """
    print("Start etl process....")
    etl_instance = GSheetsEtl(config_dict)
    etl_instance.process()

def buffer(layer, dist):
    units = " feet"
    distance = str(dist) + units

    # Output location path for the buffered layer
    output_layer = f"{layer}_buff"

    # Buffer analysis tool (input variable name, output variable name, distance type string,"FULL", "ROUND", "ALL")
    arcpy.Buffer_analysis(layer, output_layer, distance, "FULL", "ROUND", "ALL")
    print("Buffer created " + output_layer)
    return

def intersect(inter_list):
    # logging.info()
    # print the list being passed in
    print(inter_list)

    # ask the user to define an output intersect layer and store the results in a variable
    output_layer = f"{config_dict.get('proj_dir')}\WNVOutbreak.gdb\_allinter"

    # run a intersect analysis between the two buffer layer name and store the result in a variable
    # using arcpy.Intersect_analysis
    arcpy.Intersect_analysis(inter_list, output_layer)
    # print statement confirming intersect
    print("Intersect has been completed")
    # return the name of the new output layer
    return output_layer

def erase(erase_points):
    logging.info("Erasing the avoid points areas for final layer output.")
    in_features = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\_allinter"
    # in_features = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spatial_join"
    avoidpoint = erase_points
    out_feature_name = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spj_werasedpoints_layer"
    arcpy.Erase_analysis(in_features, avoidpoint, out_feature_name)
    return out_feature_name

def spatial(erase_layer):
    logging.info("Spatial joning all the addresses and the final analysis layer.")
    target_feature = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\Addresses"
    join_feature = erase_layer
    spj_file = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spatial_join"
    arcpy.SpatialJoin_analysis(target_feature, join_feature, spj_file)
    print("Spatial Join has been completed")
    return spj_file


def spatialreference(map_final):
    # Setting spatial reference (Northern Colorado State Plane) for the map document, it returns the map
    noco = 102653
    state_plane_noco = arcpy.SpatialReference(noco)
    map_final.spatialReference = state_plane_noco
    return map_final.spatialReference

def exportMap(aprx):
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
    lyr = map_final.listLayers("Target_Addresses")[0]

    # Get the existing symbol.
    sym = lyr.symbology
    sym.renderer.symbol.color = {'RGB': [255, 0, 0, 100]}
    sym.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}
    lyr.symbology = sym
    lyr.transparency = 50
    aprx.save()


    # Save all the aprx to the
    aprx.save()

    # Export final map to a pdf using the user input name.
    lyt_list.exportToPDF(f"{config_dict.get('proj_dir')}\\final_map")
    return









def main():
    logging.info("WNVOutbreak start logging:...")
    arcpy.env.workspace = f"{config_dict.get('proj_dir')}\WNVOutbreak.gdb"

    # # Setting the extent of the environment using space-delimited string
    # arcpy.env.extent="-105.2705, 40.015, 0.5, 0.25"

    # Setting overwrite to true, this will allow for previously developed files to be overwritten by a new version.
    arcpy.env.overwriteOutput = True
    LayerList = ["Mosquito_Larval_Sites", "Wetlands_Regulatory", "OSMP_Properties", "Lakes_and_Reservoirs_Boulder_County", "avoid_points"]



    # Buffer all layers
    for layer in LayerList:
        dist = 1500
        bufferlayer = buffer(layer,dist)


    # Intersect all buffered layers except avoid points layer (total of 4)
    logging.info("Intersect...")
    inter_list = ['Mosquito_Larval_Sites_buff', 'Wetlands_Regulatory_buff', 'OSMP_Properties_buff', 'Lakes_and_Reservoirs_Boulder_County_buff']
    try:
        output_intersectlayer = intersect(inter_list)
        print(f"{output_intersectlayer}")
    except:
        print("Something went wrong with the intersect all buffered layers function.")


    #Intersect all buffered layers and the avoid points layer as well
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
        TargetAddresses = arcpy.Clip_analysis("Addresses",erase_layer,"Target_Addresses")
        print("Final target address layer has been completed.")
        # Count the number of addresses to be contacted.
        address_count = arcpy.management.GetCount(TargetAddresses)
        print(f"Number of addresses to be contacted for mosquito spraying:{address_count}")
    except:
        print("Something went wrong with the clipping addresses to final analysis layer.")



    # Get Project and Set Layout
    # Save project and look at map in ArcGIS pro.
    logging.info("Creating the layout and saving final map to a pdf.")
    aprx = arcpy.mp.ArcGISProject(f"{config_dict.get('proj_dir')}WNVOutbreak.aprx")
    map = exportMap(aprx)
    logging.info("Map has been exported to PDF.")

    print("Final Map Done! Check the file folder for output.")



if __name__ == '__main__':
    global config_dict
    config_dict = setup()
    print(config_dict)
    etl()
    main()



