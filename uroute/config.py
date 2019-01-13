import os
from configparser import ConfigParser


DEFAULT_CONFIG = os.path.expanduser('~/.uroute.ini')


class Config(ConfigParser):
    def __init__(self, filename=None):
        super(Config, self).__init__()

        if filename is None:
            filename = DEFAULT_CONFIG
        self.filename = filename

        self.clear()
        self.read(filename)
