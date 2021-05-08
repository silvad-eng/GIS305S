from etl.GSheetsEtl import GSheetsEtl

# Script to help me evaluate my help documentation

config_dict={}
my_etl = GSheetsEtl(config_dict)

print(my_etl.__doc__)

help(my_etl)
