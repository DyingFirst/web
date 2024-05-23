import yaml

def readconfig():
    with open("./config.yaml", "r") as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config
