'''
Created on 19 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import is_empty
    from hra_core.collections_utils import get_or_put
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.widgets.label_widget import LabelWidget
    from hra_gui.qt.utils.windows import ErrorWindow
except ImportError as error:
    ImportErrorMessage(error, __name__)

__NOT_SET_LABEL__ = '[not set]'


class DirWidget(CompositeWidget):
    """
    widget gives ability to choose a directory
    """
    def __init__(self, parent, **params):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        get_or_put(params, 'layout', layout)
        super(DirWidget, self).__init__(parent, **params)

        LabelWidget(self, i18n_def='Directory:')

        self.__dir_label__ = LabelWidget(self, i18n_def=__NOT_SET_LABEL__,
                        sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                               QSizePolicy.Minimum))

        PushButtonWidget(self, i18n_def="Browse",
                clicked_handler=self.__clicked_handler__)

    def __clicked_handler__(self):
        _dir = self.__dir_label__.text() if self.__dir_label__.text() else '.'
        output_dir = QFileDialog.getExistingDirectory(self,
                                    caption='Choose dir', directory=_dir,
                                    options=QFileDialog.ShowDirsOnly
                                           | QFileDialog.DontResolveSymlinks)
        if output_dir:
            self.setDirectory(output_dir)

    @property
    def directory(self):
        _dir = str(self.__dir_label__.text())
        if not (is_empty(_dir) or __NOT_SET_LABEL__ == _dir):
            _dir = str(QDir(_dir[1:-1]).path())
            return _dir

    def validate(self):
        if self.directory == None:
            ErrorWindow(message="The directory must be selected !")
            return False
        return True

    def setDirectory(self, output_dir):
        """
        set directory by external code
        """
        self.__dir_label__.setText("[%s]" % output_dir)
