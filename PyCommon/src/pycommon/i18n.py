'''
Created on 04-11-2012

@author: jurek
'''
from pycore.globals import GLOBALS
from pycore.properties import Properties
from pycore.collections import replace_all_by_dict

__I18N_PROPERTIES = Properties(GLOBALS.get(I18N_FILE=GLOBALS.ITEM,
                                           PARAM1=GLOBALS.LANG),
                                _file_prefix=GLOBALS.SETTINGS_DIR,
                                _use_as_resources=GLOBALS.USE_SETTINGS_EGG)


def I18N(_id, _default=None, **params):
    i18n = __I18N_PROPERTIES.getValue(_id)
    return replace_all_by_dict(i18n, params) if i18n else _default
