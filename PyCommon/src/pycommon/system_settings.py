'''
Created on 20-10-2012

@author: jurek
'''
from pycore.io_utils import get_program_path

import configobj
from os.path import join

PROGRAM_PATH = get_program_path()


def _getItems():
    SETTINGS_DIR = "etc"
    SETTINGS_FILE = "system_settings.properties"
    MENUS_FILENAME = "menus.xml"
    PLUGINS_DIR_NAME = "plugins"

    def getItemPath(properties, item_key, defaultValue):
        for key, value in properties:
            if item_key == key:
                return join(PROGRAM_PATH, value)
        return join(PROGRAM_PATH, SETTINGS_DIR, defaultValue)

    settings_file = join(PROGRAM_PATH, SETTINGS_DIR, SETTINGS_FILE)
    properties = configobj.ConfigObj(settings_file)
    properties = properties.items()

    return (getItemPath(properties, 'menus_file', MENUS_FILENAME),
            getItemPath(properties, 'plugins_dir', PLUGINS_DIR_NAME))

(MENUS_FILE, PLUGINS_DIR) = _getItems()
