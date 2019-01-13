import os
from collections import OrderedDict
from configparser import ConfigParser


DEFAULT_CONFIG = os.path.expanduser('~/.uroute.ini')


def create_initial_config(filename):
    import webbrowser
    config = ConfigParser()
    default_browser = None

    for browser_name in webbrowser._browsers.keys():
        if browser_name == 'firefox':
            config['program:firefox'] = OrderedDict((
                ('name', 'Firefox'),
                ('command', 'firefox'),
            ))
            config['program:firefox-private'] = OrderedDict((
                ('name', 'Firefox Private Window'),
                ('command', 'firefox --private-window'),
            ))
            default_browser = 'firefox-private'
        elif browser_name == 'chromium-browser':
            config['program:chromium'] = OrderedDict((
                ('name', 'Chromium'),
                ('command', 'chromium-browser'),
            ))
            config['program:chromium-incognito'] = OrderedDict((
                ('name', 'Chromium Incognito'),
                ('command', 'chromium-browser --incognito'),
            ))

            if not default_browser:
                default_browser = 'chromium-incognito'

    if default_browser:
        config['uroute'] = {'default_program': default_browser}

    with open(filename, 'w') as config_file:
        config.write(config_file)


class Config(ConfigParser):
    def __init__(self, filename=None):
        super(Config, self).__init__()

        if filename is None:
            filename = DEFAULT_CONFIG
        self.filename = filename

        if not os.path.isfile(filename):
            dirname = os.path.dirname(filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            create_initial_config(filename)

        self.clear()
        self.read(filename)
