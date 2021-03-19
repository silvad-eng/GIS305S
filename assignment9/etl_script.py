import arcpy
import csv
import requests


# extract function
def extract():
    print("Extracting addresses from google form spreadsheets")

    r = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTaJ_1xRhGQAOSITkgn_C1wfPSnPX0BA37XuftlXVfVrpjfj4J3BHPu1soGeUtNt3XjLI1G_HT2Fy69/pub?output=csv")
    r.encoding = "utf-8"
    data = r.text
    with open(r"E:\GIS\GIS305\Lab1\Lab1\Lab1\BoulderAddresses.csv", "w") as output_file: output_file.write(data)

# transform function
def transform():
    print("Add City, State")

    transformed_file = open(r"E:\GIS\GIS305\Lab1\Lab1\Lab1\new_BoulderAddresses.csv", "w")
    transformed_file.write("X,Y,Type\n")
    with open(r"E:\GIS\GIS305\Lab1\Lab1\Lab1\BoulderAddresses.csv", "r") as partial_file:
        csv_dict = csv.DictReader(partial_file, delimiter=',')
        for row in csv_dict:
            address = row["Street Address"] + " Boulder CO"
            print(address)
            geocode_url = "http://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=" + address + \
                "&benchmark=2020&format=json"
            r = requests.get(geocode_url)

            resp_dist = r.json()
            x = resp_dist['result']['addressMatches'][0]['coordinates']['x']
            y = resp_dist['result']['addressMatches'][0]['coordinates']['y']
            transformed_file.write(f"{x},{y}, Residential\n")

    transformed_file.close()

# load function
def load():
    #Descrittion: Creates a point feature class from input table

    #Set Environment Settings
    arcpy.env.workspace= r"E:\GIS\GIS305\Lab1\Lab1\Lab1\Lab1.gdb\\"
    arcpy.env.overwriteOutput = True

    in_table = r"E:\GIS\GIS305\Lab1\Lab1\Lab1\new_BoulderAddresses.csv"
    out_feature_class = "avoid_points"
    x_coords = "X"
    y_coords = "Y"


#     Make the XY event layer....
    arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

#     Print the total rows
    print(arcpy.GetCount_management(out_feature_class))

if __name__=="__main__":
    extract()
    transform()
    load()







