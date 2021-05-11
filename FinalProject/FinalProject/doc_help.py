from etl.GSheetsEtl import GSheetsEtl

from etl.SpatialEtl import SpatialEtl

from FinalProject import finalproject

# Script to help me evaluate my help documentation

config_dict = {}
my_etl = GSheetsEtl(config_dict)
my_spatial = SpatialEtl(config_dict)
my_finalproject = finalproject

print(my_etl.__doc__)
print(my_spatial.__doc__)
print(my_finalproject.__doc__)

help(my_etl)
help(my_spatial)