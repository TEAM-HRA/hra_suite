'''
Created on 30-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import collections
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
except ImportError as error:
    ImportErrorMessage(error, __name__)


PropertySpecification = collections.namedtuple('PropertySpecification',
                                               ["name", "typename"])


class BasicDragger(object):
    """
    basic functionality for dragging widget elements
    """
    def __init__(self, _parent, _mime_id, **params):
        self.__mime_id__ = _mime_id
        self.__parent__ = _parent
        params = Params(**params)
        self.__parent__.setDragEnabled(True)
        if params.drag_only:
            if hasattr(self, 'setDragDropMode'):
                self.__parent__.setDragDropMode(QAbstractItemView.DragOnly)
        self.__objects__ = {}

    def clear(self):
        self.__objects__ = {}

    def dragObject(self, _name, _object):
        """
        method to add a value associated with a name attached
        when a user is dragging over widgets
        """
        if isinstance(_object, str):
            self.__objects__[_name] = QString(_object)
        else:
            self.__objects__[_name] = QVariant(_object)

    def startDrag(self, dropActions):
        """
        method called when dragging process starts,
        a place where all values are collected during dragging
        process; the first stored item holds information about
        names and types of the next elements
        """
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        specifications = []
        for name in sorted(self.__objects__):
            #store a name (a key) and a class name of value
            specifications.append(PropertySpecification(name,
                                self.__objects__[name].__class__.__name__))
        stream << QVariant(specifications)
        for specification in specifications:
            stream << self.__objects__[specification.name]
        mimeData = QMimeData()
        mimeData.setData(self.__mime_id__, data)
        drag = QDrag(self.__parent__)
        drag.setMimeData(mimeData)
        drag.start(supportedActions=dropActions)


class CopyDragger(BasicDragger):
    """
    dragger for copy actions
    """
    def startDrag(self):
        super(CopyDragger, self).startDrag(Qt.CopyAction)


class MoveDragger(BasicDragger):
    """
    dragger for move actions
    """
    def startDrag(self):
        super(MoveDragger, self).startDrag(Qt.MoveAction)


class BasicDropper(object):
    """
    basic functionality for dropping actions
    """
    def __init__(self, _parent, _mime_id, _drop_action, **params):
        self.__mime_id__ = _mime_id
        self.__drop_action__ = _drop_action
        _parent.setAcceptDrops(True)
        self.__objects__ = {}

    def dropEvent(self, event):
        """
        method runs when drop event happens,
        all values associated with dragging process are fetched
        in a dictionary object
        """
        if event.mimeData().hasFormat(self.__mime_id__):
            data = event.mimeData().data(self.__mime_id__)
            stream = QDataStream(data, QIODevice.ReadOnly)
            specifications = QVariant()
            #first element in data includes specification of all other
            #data that means names and data types
            stream >> specifications
            specifications = specifications.toPyObject()
            for specification in specifications:
                value = eval(specification.typename + "()")
                stream >> value
                self.__objects__[specification.name] = value
            event.setDropAction(self.__drop_action__)
            event.accept()
            return True
        else:
            event.ignore()
            return False

    def dragEnterEvent(self, event):
        """
        this method is required because before drop action
        there have to be allowed a dragging process over the widget
        """
        if event.mimeData().hasFormat(self.__mime_id__):
            event.accept()
            return True
        else:
            event.ignore()
            return False

    def dropObject(self, _name):
        """
        get a value associated with a name in a dragging process
        """
        value = self.__objects__.get(_name, None)
        return str(value) if isinstance(value, QString) else value


class CopyDropper(BasicDropper):
    """
    dropper for copy actions
    """
    def __init__(self, _parent, _mime_id, **params):
        super(CopyDropper, self).__init__(_parent, _mime_id, Qt.CopyAction,
                                          **params)


class MoveDropper(BasicDropper):
    """
    dropper for move actions
    """
    def __init__(self, _parent, _mime_id, **params):
        super(MoveDropper, self).__init__(_parent, _mime_id, Qt.MoveAction,
                                          **params)
