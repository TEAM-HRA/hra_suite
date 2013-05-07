'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.collections_utils import nvl
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ProgressDialogWidget(QProgressDialog, Common):
    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.params.label_text = nvl(self.params.label_text, 'Processing...')
        self.params.cancel_text = nvl(self.params.cancel_text, 'Abort')
        self.min_value = nvl(self.params.min_value, 0)
        self.max_value = nvl(self.params.max_value, 10000)
        self.counter = self.min_value
        super(ProgressDialogWidget, self).__init__(self.params.label_text,
                                                   self.params.cancel_text,
                                                   self.min_value,
                                                   self.max_value,
                                                   parent)
        self.setWindowTitle(nvl(self.params.title, 'Progress'))
        if params.get('not_add_widget_to_parent_layout', None) == None:
            params['not_add_widget_to_parent_layout'] = True
        prepareWidget(parent=parent, widget=self, **params)

    def increaseCounter(self, step=1):
        self.setValue(self.counter)
        self.counter = self.counter + step
        if self.counter > self.max_value:
            self.counter = 0
        self.setLabelText("{0} [{1}/{2}]".format(self.params.label_text,
                                              self.counter,
                                              self.max_value))
