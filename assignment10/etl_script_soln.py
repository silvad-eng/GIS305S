import arcpy
import requests
import csv
import json

def extract():
    print("Extracting addresses from google form spreadsheet")
    #file = urllib.request.urlopen("https://docs.google.com/spreadsheets/d/e/2PACX-1vTaJ_1xRhGQAOSITkgn_C1wfPSnPX0BA37XuftlXVfVrpjfj4J3BHPu1soGeUtNt3XjLI1G_HT2Fy69/pub?output=csv")

    r = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTaJ_1xRhGQAOSITkgn_C1wfPSnPX0BA37XuftlXVfVrpjfj4J3BHPu1soGeUtNt3XjLI1G_HT2Fy69/pub?output=csv")
    r.encoding = "utf-8"
    data = r.text
    with open(r"C:\Users\David Neufeld\Downloads\addresses.csv", "w") as output_file:
        output_file.write(data)


def transform():
    print("Add City, State")

    transformed_file = open(r"C:\Users\David Neufeld\Downloads\new_addresses.csv", "w")
    transformed_file.write("X,Y,Type\n")
    with open(r"C:\Users\David Neufeld\Downloads\addresses.csv", "r") as partial_file:
        csv_dict = csv.DictReader(partial_file, delimiter=',')
        for row in csv_dict:
            address = row["Street Address"] + " Boulder CO"
            print(address)
            geocode_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=" + address + "&benchmark=2020&format=json"
            print(geocode_url)
            r = requests.get(geocode_url)

            resp_dict = r.json()
            x = resp_dict['result']['addressMatches'][0]['coordinates']['x']
            y = resp_dict['result']['addressMatches'][0]['coordinates']['y']
            transformed_file.write(f"{x},{y},Residential\n")

    transformed_file.close()


def load():
    # Description: Creates a point feature class from input table

    # Set environment settings
    arcpy.env.workspace = r"C:\Users\David Neufeld\Documents\ArcGIS\GIS305\Projects\ModelBuilder\ModelBuilder.gdb\\"
    arcpy.env.overwriteOutput = True

    # Set the local variables
    in_table = r"C:\Users\David Neufeld\Downloads\new_addresses.csv"
    out_feature_class = "avoid_points"
    x_coords = "X"
    y_coords = "Y"


    # Make the XY event layer...
    arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

    # Print the total rows
    print(arcpy.GetCount_management(out_feature_class))

if __name__ == "__main__":
    extract()
    transform()
    load()