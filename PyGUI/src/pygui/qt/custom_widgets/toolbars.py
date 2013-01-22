'''
Created on 19-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import collections
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.collections import all_true_values
    from pycore.collections import nvl
    from pycommon.actions import ActionSpec
    from pygui.qt.actions.actions_utils import create_action
    from pygui.qt.utils.widgets import Common
    from pygui.qt.utils.widgets import WidgetCommon
    from pygui.qt.utils.widgets import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ToolButtonCommon(QToolButton, Common):

    def __init__(self, parent, **params):
        super(ToolButtonCommon, self).__init__(parent)
        if params.get('add_widget_to_parent', None) == None:
            params['add_widget_to_parent'] = False
        if params.get('not_add_widget_to_parent_layout', None) == None:
            params['not_add_widget_to_parent_layout'] = True
        prepareWidget(parent=parent, widget=self, **params)
        action = params.get('action', None)
        if action:
            self.setDefaultAction(action)


class ToolBarCommon(QToolBar, Common):
    def __init__(self, parent, _button_types=[], _check_fields=[], **params):
        if params.get('not_add_widget_to_parent_layout', None) == None:
            params['not_add_widget_to_parent_layout'] = True
        super(ToolBarCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)

        #to avoid some weird behaviour which manifests in including
        #in this toolbar buttons from the previous one
        button_types = _button_types[:]

        button_type_classes = [_button.__class__ for _button in button_types]
        for _class in ToolButtonType.__subclasses__():  # @UndefinedVariable
            button_type = _class()
            if _class not in button_type_classes and \
                (all_true_values(button_type, _check_fields) or
                 len(_check_fields) == 0):
                button_types.append(button_type)

        for _button_type in button_types:
            create_toolbar_button(parent, self, _button_type, **params)


DefaultToolButtonType = collections.namedtuple('ToolButtonType',
    'active operational checkable handler_name icon_id title handler_callable_name') # @IgnorePep8


def create_toolbar_button(parent, toolbar, button_type, **params):
    params = Params(**params)
    params.handler = getattr(params, button_type.handler_callable_name, None)
    if params.handler == None and button_type.handler_name:
        if hasattr(parent, button_type.handler_name):
            params.handler = getattr(parent, button_type.handler_name)
        elif hasattr(parent.parentWidget(), button_type.handler_name):
            params.handler = getattr(parent.parentWidget(),
                                     button_type.handler_name)
        elif hasattr(params, button_type.handler_name):
            params.handler = getattr(params, button_type.handler_name)
    title = nvl(params.button_title, button_type.title)
    actionSpec = ActionSpec(iconId=button_type.icon_id,
                                 handler=params.handler,
                                 title=title)
    toolbar.addWidget(ToolButtonCommon(toolbar,
                        action=create_action(toolbar, actionSpec)))


class ToolBarManager(WidgetCommon):
    """
    this class give ability to join toolbars as a one widget
    """
    def __init__(self, parent=None, *toolbar_classes, **params):
        super(ToolBarManager, self).__init__(parent, **params)

        #toolbars cannot set up their own layouts, one have to remove
        #this parameter to avoid it's propagating to toolbars classes,
        #if there is no layout passed for ToolBarManager then default one
        #is created
        layout = params.pop('layout', QHBoxLayout())
        self.setLayout(layout)

        for toolbar_class in toolbar_classes:
            self.layout().addWidget(toolbar_class(self, **params))


class CheckUncheckToolBarWidget(ToolBarCommon):
    def __init__(self, parent=None, **params):
        super(CheckUncheckToolBarWidget, self).__init__(parent,
                                                _check_fields=['checkable'],
                                                 **params)


class OperationalToolBarWidget(ToolBarCommon):
    def __init__(self, parent=None, _button_types=[], **params):
        super(OperationalToolBarWidget, self).__init__(parent,
                                                _check_fields=['operational'],
                                                **params)


class ToolButtonType(object):
    def __init__(self, default, **params):
        params = Params(**params)
        self.active = nvl(params.active, default.active)
        self.operational = nvl(params.operational, default.operational)
        self.checkable = nvl(params.checkable, default.checkable)
        self.handler_name = nvl(params.handler_name, default.handler_name)
        self.icon_id = nvl(params.icon_id, default.icon_id)
        self.title = nvl(params.title, default.title)
        self.handler_callable_name = default.handler_callable_name


class MaximumToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_maximum_handler', 'toolbar_maximum_button',
            'Maximize', 'toolbar_maximum_handler_callable')
        super(MaximumToolButton, self).__init__(default, **params)


class MinimumToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_minimum_handler', 'toolbar_minimum_button',
            'Minimize', 'toolbar_minimum_handler_callable')
        super(MinimumToolButton, self).__init__(default, **params)


class CloseToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_close_handler', 'toolbar_close_button',
            'Close', 'toolbar_close_handler_callable')
        super(CloseToolButton, self).__init__(default, **params)


class HideToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_hide_handler', 'toolbar_hide_button',
            'Hide', 'toolbar_hide_handler_callable')
        super(HideToolButton, self).__init__(default, **params)


class CheckToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, False, True,
            'toolbar_check_handler', 'toolbar_check_button',
            'Check', 'toolbar_check_handler_callable')
        super(CheckToolButton, self).__init__(default, **params)


class UncheckToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, False, True,
            'toolbar_uncheck_handler', 'toolbar_uncheck_button',
            'Uncheck', 'toolbar_uncheck_handler_callable')
        super(UncheckToolButton, self).__init__(default, **params)
