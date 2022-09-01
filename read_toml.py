import toml
import configparser


class read_config:
    def __init__(self, path="config.toml") -> None:
        self.conf = configparser.ConfigParser()
        self.conf.read(path)
    #def 



print(toml.load("config.toml"))

conf = configparser.ConfigParser()
conf.read("config.toml")
print(conf["default"])