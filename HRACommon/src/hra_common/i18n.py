'''
Created on 04-11-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from hra_core.globals import GLOBALS
    from hra_core.properties import Properties
    from hra_core.collections_utils import replace_all_by_dict
except ImportError as error:
    ImportErrorMessage(error, __name__)

__I18N_PROPERTIES = Properties(GLOBALS.get(I18N_FILE=GLOBALS.ITEM,
                                           PARAM1=GLOBALS.LANG),
                                _file_prefix=GLOBALS.SETTINGS_DIR,
                                _use_as_resources=GLOBALS.USE_SETTINGS_EGG)


def I18N(_id, _default=None, **params):
    if _id:
        i18n = __I18N_PROPERTIES.getValue(_id)
        if i18n:
            return replace_all_by_dict(i18n, params)
    return "" if _default == None else _default
