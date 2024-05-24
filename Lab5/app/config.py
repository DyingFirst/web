import yaml
from connector_db import MySQL


def readconfig():
    with open("./config.yaml", "r") as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


cfg = readconfig()
db = MySQL(cfg)
