'''
Created on 19 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.widgets.label_widget import LabelWidget
    from pygui.qt.utils.windows import ErrorWindow
except ImportError as error:
    ImportErrorMessage(error, __name__)


class DirWidget(CompositeCommon):
    """
    widget gives ability to choose a directory
    """
    def __init__(self, parent, **params):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        get_or_put(params, 'layout', layout)
        super(DirWidget, self).__init__(parent, **params)

        LabelWidget(self, i18n_def='Directory:')

        self.__dir_label__ = LabelWidget(self, i18n_def='[not set]',
                        sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                               QSizePolicy.Minimum))

        PushButtonCommon(self, i18n_def="Browse",
                clicked_handler=self.__clicked_handler__)

    def __clicked_handler__(self):
        _dir = self.__dir_label__.text() if self.__dir_label__.text() else '.'
        output_dir = QFileDialog.getExistingDirectory(self,
                                        caption='Choose dir', directory=_dir)
        if output_dir:
            self.__dir_label__.setText("[%s]" % output_dir)

    @property
    def directory(self):
        _dir = self.__dir_label__.text()
        return None if _dir == None or len(_dir) == 0 else _dir

    def validate(self):
        if not self.directory:
            ErrorWindow(message="The directory must be selected !")
            return False
        return True
