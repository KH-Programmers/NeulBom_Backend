from configparser import ConfigParser


def getConfig() -> ConfigParser:
    config = ConfigParser()
    config.read(filenames="config.ini", encoding="utf-8")
    return config
