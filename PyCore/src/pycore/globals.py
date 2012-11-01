'''
Created on 09-09-2012

@author: jurek
'''
import optparse
import sys
from os.path import join
from os.path import dirname
from pycore.collections import get_any_key
from pycore.properties import Properties


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

    # a value of ITEM property doesn't matter,
    # this property is used as a marker in a situation
    # when one wish to acquire a property from GLOBALS
    # class without defining such property in that class
    # but defining such property only in the properties file,
    # so to get such property one have to pass the name of the needed
    # one as a parameter (with the same name as the required property)
    # of the get method as the following example shows:
    # GLOBALS.get(ICONS_FILE=GLOBALS.ITEM)
    # which is equivalent to
    # GLOBALS.ICONS_FILE
    # but without explicit definition of the ICONS_FILE property
    ITEM = True

    def get(self, **params):
        #to acquire a value of a field dynamically
        #warning ! the assumption that only one parameter is passed
        return getattr(self, get_any_key(**params)) \
                        if len(params) == 1 else None

GLOBALS = Globals()


def __load_settings_file():
    for key, value in Properties(GLOBALS.SETTINGS_FILE).items:
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
