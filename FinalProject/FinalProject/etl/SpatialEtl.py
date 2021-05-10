"""
    Defined functions for extract, transform and load.

    passing parameters: self, configuration dictionary
    returns:
        Print statements to verify the function is working correctly by inputting the results into the file folder
        in the yaml file.

"""
class SpatialEtl:

    def __init__(self, config_dict):
        self.config_dict = config_dict

    def extract(self):
        """
        Extracts addresses from google form (avoid point layer) and puts them in the project directory (yaml file)
        """
        print(f"Extracting data from {self.config_dict.get('remote_url')}" f" to {self.config_dict.get('proj_dir')}")

    def transform(self):
        """
        Transforms the addresses from google form using a geocoder into a readablel XY Table for ArcGIS Pro.
        """
        print(f"Transforming {self.config_dict.get('proj_dir')}")

    def load(self):
        """
        Loads the final avoid point layer into the main function for analysis.
        """
        print(f"Loading data into {self.config_dict.get('proj_dir')}")