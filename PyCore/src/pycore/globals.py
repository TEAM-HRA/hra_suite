'''
Created on 09-09-2012

@author: jurek
'''
import optparse
import sys
from os.path import join
from os.path import dirname
import configobj


class Globals(object):
    __parser = optparse.OptionParser()
    __parser.add_option("-s", "--settings_file", type="string")
    __opts, __args = __parser.parse_args()
    PROGRAM_DIR = sys.path[0]
    SETTINGS_FILE = __opts.settings_file \
        if __opts.settings_file else join(PROGRAM_DIR, "settings.properties")
    SETTINGS_DIR = dirname(SETTINGS_FILE)

    DATA_DIR = None
    EXT_MASK = None
    NUMPY_USAGE = None
    MENUS_FILE = None
    PLUGINS_DIR = None

GLOBALS = Globals()


def __load_settings_file():
    properties = configobj.ConfigObj(GLOBALS.SETTINGS_FILE)
    properties = properties.items()
    for key, value in properties:
        if value.lower() in ("false", "true"):
            value = bool("true" == value.lower())
        absolute = False
        if key.endswith("_ABSOLUTE"):
            key = key[:-len("_ABSOLUTE")]
            absolute = True

        setattr(GLOBALS, key,
                join(GLOBALS.SETTINGS_DIR, value)
                if absolute == False
                    and (key.endswith("_DIR") or key.endswith("_FILE"))
                else value)

__load_settings_file()
