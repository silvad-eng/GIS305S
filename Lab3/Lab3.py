import yaml
import logging
import arcpy

from etl.GSheetsEtl import GSheetsEtl

def setup():
    with open('config_dict/wnvoutbreak.yaml') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

        logging.basicConfig(level=logging.DEBUG, filename= "wnvoutbreak.log", filemode="w", format='%(name)s - ''%(levelname)s - ''%(message)s')

    return config_dict


def etl():
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

def spatial(erase_layer):
    target_feature = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\Addresses"
    join_feature = erase_layer
    spj_file = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spatial_join"
    arcpy.SpatialJoin_analysis(target_feature, join_feature, spj_file)
    print("Spatial Join has been completed")
    return spj_file

def erase(erase_points):
    in_features = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\_allinter"
    # in_features = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spatial_join"
    avoidpoint = erase_points
    out_feature_name = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spj_werasedpoints_layer"
    arcpy.Erase_analysis(in_features, avoidpoint, out_feature_name)
    return out_feature_name

# def spatialselection():


def exportMap(aprx):
    map_final = aprx.listMaps()[0]

    #Setting spatial reference (Northern Colorado State Plane) for the map document.
    state_plane_noco = arcpy.SpatialReference(102653)
    map_final.spatialReference = state_plane_noco

    #List Map Layout in WNVOutbreak Project
    lyt_list = aprx.listLayouts()[0]
    sub_title = input("Please enter the name for the output map: ")
    final_analysisname = input(str("Enter the name of the final name: "))
    pdf_filename = final_analysisname.pdf
    print(lyt_list.name)

    for el in lyt_list.listElements():
        print(el.name)
        if "Title" in el.name:
            el.text = el.text + " " + sub_title

    # Save all the aprx to the
    aprx.save()

    # Export final map to a pdf using the user input name.
    lyt_list.exportToPDF(f"{config_dict.get('proj_dir')}\pdf_filename")
    return


def main():
    logging.info("WNVOutbreak start logging:...")
    arcpy.env.workspace = f"{config_dict.get('proj_dir')}\WNVOutbreak.gdb"

    #aprx = arcpy.mp.ArcGISProject(f"{config_dict.get('proj_dir')}WNVOutbreak.gdb.aprx")
    arcpy.env.overwriteOutput = True

    LayerList = ["Mosquito_Larval_Sites", "Wetlands_Regulatory", "OSMP_Properties", "Lakes_and_Reservoirs_Boulder_County", "avoid_points"]
    print(LayerList)

    #buffer
    for layer in LayerList:
        dist = 1500
        bufferlayer = buffer(layer,dist)


    #Intersect all buffered layers except avoid points layer (total of 4)
    logging.info("Intersect...")
    inter_list = ['Mosquito_Larval_Sites_buff', 'Wetlands_Regulatory_buff', 'OSMP_Properties_buff', 'Lakes_and_Reservoirs_Boulder_County_buff']
    output_intersectlayer = intersect(inter_list)
    print(f"{output_intersectlayer}")

    #Intersect all buffered layers and the avoid points layer as well
    inter_list2 =["_allinter", "avoid_points_buff"]
    outputlayer_avpt=f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\intersect_avpt"
    arcpy.Intersect_analysis(inter_list2, outputlayer_avpt)
    print("Intersect avoid points layer complete.")


    #Erase
    logging.info("Erase new address points from spatial join layer.")
    erase_points = "intersect_avpt"
    erase_layer = erase(erase_points)
    print(f"Erases new address file from spatial join: {erase_layer}")

    # Spatialjoin
    logging.info("Spatial Join all buffered layers.")
    finaloutput_spjlayer = spatial(erase_layer)
    print(f"New Spatial Join Layer named: {finaloutput_spjlayer}")

    # Select Addresses within the spatial join that will be contacted for mosquito spraying
    # addresses_final = arcpy.SelectLayerByLocation_management('')


    #Get Project and Set Layout
    # Save project and look at map in arc pro.
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


