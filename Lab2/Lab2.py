import yaml
import arcpy

from etl.GSheetsEtl import GSheetsEtl

def setup():
    with open('config_dict/wnvoutbreak.yaml') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

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

def spatial(output_intersectlayer):
    target_feature = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\Addresses"
    join_feature = output_intersectlayer
    spj_file = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spatial_join"
    arcpy.SpatialJoin_analysis(target_feature, join_feature, spj_file)
    print("Spatial Join has been completed")
    return spj_file

def erase(erase_points):
    in_features = r"C:\Users\chica\Documents\ArcGIS\Projects\WNVOutbreak\WNVOutbreak.gdb\spatial_join"
    avoidpoint= erase_points
    out_feature_name = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\spj_werasedpoints_layer"
    arcpy.Erase_analysis(in_features, avoidpoint, out_feature_name)
    return out_feature_name




def main():
    arcpy.env.workspace = f"{config_dict.get('proj_dir')}\WNVOutbreak.gdb"
    #aprx = arcpy.mp.ArcGISProject(f"{config_dict.get('proj_dir')}WNVOutbreak.gdb.aprx")
    arcpy.env.overwriteOutput = True

    LayerList = ["Mosquito_Larval_Sites", "Wetlands_Regulatory", "OSMP_Properties", "Lakes_and_Reservoirs_Boulder_County", "avoid_points"]
    print(LayerList)

    #buffer
    for layer in LayerList:
        dist= 1500
        bufferlayer = buffer(layer,dist)


    #Intersect
    inter_list = ['Mosquito_Larval_Sites_buff', 'Wetlands_Regulatory_buff', 'OSMP_Properties_buff', 'Lakes_and_Reservoirs_Boulder_County_buff']
    output_intersectlayer = intersect(inter_list)
    print(f"{output_intersectlayer}")

    #Spatialjoin
    output_spjlayer = spatial(output_intersectlayer)
    print(f"New Spatial Join Layer named: {output_spjlayer}")

    #Erase
    erase_points = r"C:\Users\chica\Documents\ArcGIS\Projects\WNVOutbreak\WNVOutbreak.gdb\avoid_points_buff"
    erase_layer = erase(erase_points)
    print(f"Erases newaddress file from spatial join: {erase_layer}")

    #Get Project and Set Layout
    # Save project and look at map in arc pro.
    aprx = arcpy.mp.ArcGISProject(f"{config_dict.get('proj_dir')}WNVOutbreak.aprx")
    map_final = aprx.listMaps()[0]
    # map_final.addDataFromPath(f"{config_dict.get('proj_dir')}erase_layer")
    aprx.save





if __name__ == '__main__':
    global config_dict
    config_dict = setup()
    print(config_dict)
    etl()
    main()



