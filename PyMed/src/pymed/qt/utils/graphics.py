'''
Created on 22-11-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.resources import is_resource


def get_resource_as_icon(iconfilename_or_resource):
    """
    if parameter is simple string then it is used as parameter for QIcon
    object, if parameter is of resource type then a conversion from a resource
    object (usually represented by string of bytes) to QIcon object
    is taken place, the conversion is possible if resource represents some
    real image object
    """
    if is_resource(iconfilename_or_resource):
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(iconfilename_or_resource.data))
        return QIcon(pixmap)
    else:
        return QIcon(iconfilename_or_resource)
