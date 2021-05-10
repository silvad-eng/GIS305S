import arcpy
import requests
import csv

from etl.SpatialEtl import SpatialEtl


class GSheetsEtl(SpatialEtl):

    """
    GSheetsEtl performs an extract, transform and load process using a URL to a
    google spreadsheet. The spreadsheet must contain an address and zipcode column. It imports classes
    from the SpatialEtl file and adds

    parameters:
    config_dict(dictionary): A dictionary containing a remote_url key to the google
    spreadsheet and web geocoding service.
    SpatialEtl: calls the
    returns: avoid points layer (XYTable)


    """

    config_dict = None
    def __init__(self, config_dict):
        super().__init__(config_dict)

    def extract(self):
        """
        Extracting data from a google spreadsheet and save it as a local file.
        parameters: yaml file google form url
        returns: csv
        """
        print("Extracting addresses from google form spreadsheet")
        r = requests.get(self.config_dict.get('remote_url'))
        r.encoding = "utf-8"
        data = r.text
        with open(f"{self.config_dict.get('proj_dir')}addresses.csv", "w") as output_file:
            output_file.write(data)

    # transform function
    def transform(self):
        """
        Takes the file from the file folder, processes addresses through a geocoder.
        Saves the file as new csv file.

        Adds city and state to the address then passing it through the geocoder and requesting
        XY coordinates, returning a json file.

        parameter: self, remote url prefix and suffix (yaml file)
        returns: csv with x and y coordinates to be used as the avoid points layer in finalproject.py main function

        """
        print("Add City, State")
        geocoder_prefix_url = self.config_dict.get('geocoder_prefix_url')
        geocoder_suffix_url = self.config_dict.get('geocoder_suffix_url')
        transformed_file = open(f"{self.config_dict.get('proj_dir')}new_addresses.csv", "w")
        transformed_file.write("X,Y,Type\n")
        with open(f"{self.config_dict.get('proj_dir')}addresses.csv", "r") as partial_file:
            csv_dict = csv.DictReader(partial_file, delimiter=',')
            for row in csv_dict:
                address = row["Street Address"] + " Boulder CO"
                print(address)
                geocode_url = f"{geocoder_prefix_url}{address}{geocoder_suffix_url}"
                print(geocode_url)
                r = requests.get(geocode_url)

                resp_dist = r.json()
                x = resp_dist['result']['addressMatches'][0]['coordinates']['x']
                y = resp_dist['result']['addressMatches'][0]['coordinates']['y']
                transformed_file.write(f"{x},{y}, Residential\n")

        transformed_file.close()

    # load function
    def load(self):
        """
         Creates a point feature class from  the input table by creating a XY event layer and is then
         called in finalproject.py main's-but is loaded into the project directory (found in the yaml file).

         parameters: self, project directory (found in yaml file)
         returns: XY Table to ArcGIS Pro and a count of the number addresses inputted google form
        """

        # Set Environment Settings
        arcpy.env.workspace = f"{self.config_dict.get('proj_dir')}"
        arcpy.env.overwriteOutput = True

        in_table = r"C:\Users\chica\Documents\ArcGIS\Projects\WNVOutbreak\new_addresses.csv"
        out_feature_class = f"{self.config_dict.get('proj_dir')}WNVOutbreak.gdb\\avoid_points"
        print(f"{out_feature_class}")
        print("Avoid points file has been created.")
        x_coords = "X"
        y_coords = "Y"

        # Make the XY event layer using arcpy's XYTabletoPoint function.
        arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

        #     Print the total rows
        print(arcpy.GetCount_management(out_feature_class))

    def process(self):
        """
        Start the processes of extract, transform and load.

        """
        self.extract()
        self.transform()
        self.load()