'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import ComboBoxCommon
    from pygui.qt.widgets.label_widget import LabelWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class DecimalPrecisionWidget(CompositeCommon):
    MAX_PRECISION = 36
    """
    widget aimed to choose precision (ans sclae) for decimal numbers
    """
    def __init__(self, parent, **params):
        params['layout'] = QHBoxLayout()
        super(DecimalPrecisionWidget, self).__init__(parent, **params)
        LabelWidget(self, i18n_def='Precision')

        self.__precision_choice__ = ComboBoxCommon(self,
                           clicked_handler=self.__precision_change_handler__,
                           sizePolicy=QSizePolicy(QSizePolicy.Fixed,
                                                  QSizePolicy.Fixed))
        for row in range(1, DecimalPrecisionWidget.MAX_PRECISION):
            self.__precision_choice__.addItem(str(row))
        precision = params.get('precision',
                               DecimalPrecisionWidget.MAX_PRECISION) - 1
        self.__precision_choice__.setCurrentIndex(precision)

        LabelWidget(self, i18n_def='.',
                    sizePolicy=QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Fixed))
        self.__scale_choice__ = ComboBoxCommon(self,
                            sizePolicy=QSizePolicy(QSizePolicy.Fixed,
                                                  QSizePolicy.Fixed))
        self.__rescale__()
        scale = params.get('scale', None)
        if scale:
            if scale <= self.__precision_choice__.count():
                self.__precision_choice__.setCurrentIndex(scale - 1)
        self.layout().addStretch(1)

    def __precision_change_handler__(self, idx):
        self.__rescale__()

    @property
    def scale(self):
        return self.__scale_choice__.currentIndex()

    @property
    def precision(self):
        return self.__precision_choice__.currentIndex() + 1

    def __rescale__(self):
        if hasattr(self, '__scale_choice__'):
            self.__scale_choice__.clear()

            # 2 spaces are important to correctly set up a widget width
            self.__scale_choice__.addItem('0  ')

            for row in range(1, self.__precision_choice__.currentIndex() + 1):
                self.__scale_choice__.addItem(str(row))
