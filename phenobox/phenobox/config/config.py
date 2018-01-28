from ConfigParser import ConfigParser

cfg = None  #:Global variable to hold the config object after it has been loaded


def load_config(path):
    """
    parses the given config and assigns the resulting object to a global variable of this module

    :param path: The path to the config file

    :return: None
    """
    cfg_parser = ConfigParser()
    cfg_parser.read(path)
    global cfg
    cfg = cfg_parser
