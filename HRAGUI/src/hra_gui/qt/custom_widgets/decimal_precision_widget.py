'''
Created on 23-03-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.combo_box_widget import ComboBoxWidget
    from hra_gui.qt.widgets.label_widget import LabelWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class DecimalPrecisionWidget(CompositeWidget):
    MAX_PRECISION = 36
    """
    widget aimed to choose precision (and scale) for decimal numbers
    """
    def __init__(self, parent, **params):
        params['layout'] = QHBoxLayout()
        super(DecimalPrecisionWidget, self).__init__(parent, **params)
        LabelWidget(self, i18n_def='Precision')

        self.__precision_choice__ = ComboBoxWidget(self,
                           clicked_handler=self.__precision_change_handler__,
                           sizePolicy=QSizePolicy(QSizePolicy.Fixed,
                                                  QSizePolicy.Fixed))
        for row in range(1, DecimalPrecisionWidget.MAX_PRECISION):
            self.__precision_choice__.addItem(str(row))
        precision = params.get('precision',
                               DecimalPrecisionWidget.MAX_PRECISION)
        self.__precision_choice__.setCurrentIndex(precision - 1)

        LabelWidget(self, i18n_def='.',
                    sizePolicy=QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Fixed))
        self.__scale_choice__ = ComboBoxWidget(self,
                            sizePolicy=QSizePolicy(QSizePolicy.Fixed,
                                                  QSizePolicy.Fixed))
        self.__rescale__()
        scale = params.get('scale', None)
        if scale:
            if scale <= self.__scale_choice__.count():
                self.__scale_choice__.setCurrentIndex(scale)
        self.layout().addStretch(1)

    def __precision_change_handler__(self, idx):
        self.__rescale__()

    @property
    def scale(self):
        return self.__scale_choice__.currentIndex()

    def setScale(self, _scale):
        self.__scale_choice__.setCurrentIndex(_scale)

    @property
    def precision(self):
        return self.__precision_choice__.currentIndex() + 1

    def setPrecision(self, _precision):
        self.__precision_choice__.setCurrentIndex(_precision - 1)

    def __rescale__(self):
        if hasattr(self, '__scale_choice__'):
            self.__scale_choice__.clear()

            # 2 spaces are important to correctly set up a widget width
            self.__scale_choice__.addItem('0  ')

            for row in range(1, self.__precision_choice__.currentIndex() + 1):
                self.__scale_choice__.addItem(str(row))
