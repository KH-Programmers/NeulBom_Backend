from configparser import ConfigParser


def GetConfig() -> ConfigParser:
    config = ConfigParser()
    config.read(filenames="config.ini", encoding="utf-8")
    return config
