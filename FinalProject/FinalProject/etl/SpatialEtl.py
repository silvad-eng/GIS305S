"""Defined functions for extract, transform and load. Passing parameters of self, configuration directory.
    returns:
        Print statements to verify the function is working correctly by inputting the results into the file folder
        in the yaml file.

"""
class SpatialEtl:

    def __init__(self, config_dict):
        self.config_dict = config_dict

    def extract(self):
        print(f"Extracting data from {self.config_dict.get('remote_url')}" f" to {self.config_dict.get('proj_dir')}")

    def transform(self):
        print(f"Transforming {self.config_dict.get('proj_dir')}")

    def load(self):
        print(f"Loading data into {self.config_dict.get('proj_dir')}")