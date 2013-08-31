'''
Created on 19-01-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import collections
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_core.collections_utils import nvl
    from hra_common.actions import ActionSpec
    from hra_gui.qt.actions.actions_utils import create_action
    from hra_gui.qt.widgets.commons import Common
    from hra_gui.qt.widgets.commons import prepareWidget
    from hra_gui.qt.widgets.commons import CommonWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


OPERATIONAL_BUTTON_GROUP = 'operational'
CHECKABLE_BUTTON_GROUP = 'checkable'


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
    def __init__(self, parent, _button_types=[], _check_groups=[], **params):
        if params.get('not_add_widget_to_parent_layout', None) == None:
            params['not_add_widget_to_parent_layout'] = True
        super(ToolBarCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)

        #to avoid some weird behaviour which manifests in including
        #in this toolbar buttons from the previous one
        button_types = _button_types[:]

        exclude_buttons_classes = params.get('excluded_buttons', None)
        button_type_classes = [_button.__class__ for _button in button_types]
        for _class in ToolButtonType.__subclasses__():  # @UndefinedVariable
            #some buttons could be excluded
            if exclude_buttons_classes:
                if _class in exclude_buttons_classes:
                    continue
            button_type = _class()
            group_ok = False
            if len(_check_groups) > 0 and len(button_type.button_groups) > 0:
                for check_group in _check_groups:
                    if check_group in button_type.button_groups:
                        group_ok = True
            if _class not in button_type_classes and \
                (len(_check_groups) == 0 or group_ok):
                button_types.append(button_type)

        for _button_type in button_types:
            create_toolbar_button(parent, self, _button_type, **params)


DefaultToolButtonType = collections.namedtuple('ToolButtonType',
    'active button_groups handler_name icon_id title handler_callable_name')


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
    handler = params.handler

    #give ability to call addition toolbar handler after proper button handler
    if button_type.handler_callable_name and \
        hasattr(button_type, 'after_toolbar_handler'):
        class ActionToolbarHandler():
            def __init__(self, button_handler, toolbar, after_toolbar_handler):
                self.__button_handler__ = button_handler
                self.__toolbar__ = toolbar
                self.__after_toolbar_handler__ = after_toolbar_handler

            def __call__(self):
                self.__button_handler__()
                self.__after_toolbar_handler__(toolbar)

        #replace button handler with toolbar button handler
        handler = ActionToolbarHandler(handler, toolbar,
                                getattr(button_type, 'after_toolbar_handler'))

    actionSpec = ActionSpec(iconId=button_type.icon_id, handler=handler,
                                 title=title)
    toolbar.addWidget(ToolButtonCommon(toolbar,
                        action=create_action(toolbar, actionSpec)))


class ToolBarManager(CommonWidget):
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
                                    _check_groups=[CHECKABLE_BUTTON_GROUP],
                                    **params)


class OperationalToolBarWidget(ToolBarCommon):
    def __init__(self, parent=None, _button_types=[], **params):
        super(OperationalToolBarWidget, self).__init__(parent,
                                    _check_groups=[OPERATIONAL_BUTTON_GROUP],
                                    **params)


class ToolButtonType(object):
    def __init__(self, default, **params):
        params = Params(**params)
        self.active = nvl(params.active, default.active)
        self.button_groups = nvl(params.button_groups, default.button_groups)
        self.handler_name = nvl(params.handler_name, default.handler_name)
        self.icon_id = nvl(params.icon_id, default.icon_id)
        self.title = nvl(params.title, default.title)
        self.handler_callable_name = default.handler_callable_name


class MaximumToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [OPERATIONAL_BUTTON_GROUP],
            'toolbar_maximum_handler', 'toolbar_maximum_button',
            'Maximize', 'toolbar_maximum_handler_callable')
        super(MaximumToolButton, self).__init__(default, **params)


class RestoreToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [OPERATIONAL_BUTTON_GROUP],
            'toolbar_restore_handler', 'toolbar_restore_button',
            'Restore', 'toolbar_restore_handler_callable')
        super(RestoreToolButton, self).__init__(default, **params)


class CloseToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [OPERATIONAL_BUTTON_GROUP],
            'toolbar_close_handler', 'toolbar_close_button',
            'Close', 'toolbar_close_handler_callable')
        super(CloseToolButton, self).__init__(default, **params)

    def after_toolbar_handler(self, toolbar):
        """
        when a toolbar is detached (floatable feature) from the parent widget
        then close button closes the parent as usual but not the toolbar
        itself, this method does it
        """
        toolbar.close()


#class HideToolButton(ToolButtonType):
#    def __init__(self, **params):
#        default = DefaultToolButtonType(True, [OPERATIONAL_BUTTON_GROUP],
#            'toolbar_hide_handler', 'toolbar_hide_button',
#            'Hide', 'toolbar_hide_handler_callable')
#        super(HideToolButton, self).__init__(default, **params)


class CheckToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [CHECKABLE_BUTTON_GROUP],
            'toolbar_check_handler', 'toolbar_check_button',
            'Check', 'toolbar_check_handler_callable')
        super(CheckToolButton, self).__init__(default, **params)


class UncheckToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [CHECKABLE_BUTTON_GROUP],
            'toolbar_uncheck_handler', 'toolbar_uncheck_button',
            'Uncheck', 'toolbar_uncheck_handler_callable')
        super(UncheckToolButton, self).__init__(default, **params)
