'''
Created on 24-11-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import QString
    from pycommon.i18n import I18N
except ImportError as error:
    ImportErrorMessage(error, __name__)


def QT_I18N(_id, _default=None, **params):
    return QString(I18N(_id, _default, **params))


def title_I18N(target, _id, _default, **params):
    target.setTitle(QT_I18N(_id, _default=_default, **params))


def text_I18N(target, _id, _default, **params):
    target.setText(QT_I18N(_id, _default=_default, **params))
