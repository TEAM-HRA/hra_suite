'''
Created on 09-09-2012

@author: jurek
'''
import argparse
import sys
from os.path import join
from os.path import dirname
from pycore.collections import get_keys_for_value
from pycore.collections import get_for_regexpr
from pycore.properties import Properties
from pycore.resources import get_application_settings
from pycore.resources import is_resource


class Globals(object):

    to_bool = lambda p: True if p.title() == "True" else False

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--settings_egg",
                        help="give an egg for settings of application", # @IgnorePep8
                        default="")
    parser.add_argument("-u", "--use_settings_egg", default=True,
                        type=to_bool)
    parser.add_argument("-s", "--settings_file", default="")
    parser.add_argument("-l", "--lang", default="en")
    parser.add_argument("-m", "--start_menu_ident", default="")
    parser.add_argument("-d", "--debug", default=False, type=to_bool)
    parser.add_argument("-n", "--use_numpy_equivalent", type=to_bool)
    __args = parser.parse_args()

    USE_NUMPY_EQUIVALENT = __args.use_numpy_equivalent
    USE_SETTINGS_EGG = __args.use_settings_egg
    #if a parameter starts with a phrase 'use' it's value has bool type,
    #otherwise string, 'very intuitive bahaviour'
    DEBUG = __args.debug
    if len(__args.settings_egg) > 0:
        sys.path.insert(0, __args.settings_egg)
        USE_SETTINGS_EGG = True

    if USE_SETTINGS_EGG:
        SETTINGS_FILE = get_application_settings()
        SETTINGS_DIR = None
    else:
        PROGRAM_DIR = sys.path[0]
        SETTINGS_FILE = __args.settings_file \
        if __args.settings_file else join(PROGRAM_DIR, "settings.properties")
        SETTINGS_DIR = dirname(SETTINGS_FILE)

    LANG = __args.lang

    DATA_DIR = None
    EXT_MASK = None
    MENUS_FILE = None
    PLUGINS_FILE = None
    PLUGINS_DIR = None
    START_MENU_ID = __args.start_menu_ident \
                    if len(__args.start_menu_ident) > 0 else None

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
    MAIN_WINDOW_NAME = "MainWindow"
    WORKSPACE_NAME = "MedWorkspace"
    TAB_MAIN_NAME = "Main"

    def get(self, **params):
        attr = get_keys_for_value(params, GLOBALS.ITEM, _one_key_only=True)
        if not hasattr(self, attr):
            return None

        value = getattr(self, get_keys_for_value(params, GLOBALS.ITEM,
                                                 _one_key_only=True))
        if len(params) > 1:
            param_keys = get_for_regexpr(params.keys(), '^PARAM[0-9]*$')
            if param_keys:
                for key in param_keys:
                    if is_resource(value):
                        value.resource = \
                            value.resource.replace("{" + key[5:] + "}",
                                                   params[key])
                    else:
                        value = value.replace("{" + key[5:] + "}", params[key])

        return value

GLOBALS = Globals()
for key, value in Properties(GLOBALS.SETTINGS_FILE,
                             _file_prefix=GLOBALS.SETTINGS_DIR,
                             _check_booleans=True,
                             _use_as_resources=GLOBALS.USE_SETTINGS_EGG).items:
    setattr(GLOBALS, key, value)
