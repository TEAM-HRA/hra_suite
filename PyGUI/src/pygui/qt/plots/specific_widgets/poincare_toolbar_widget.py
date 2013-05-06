'''
Created on 6 maj 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
from pygui.qt.custom_widgets.toolbars import ToolButtonType,\
    DefaultToolButtonType
try:
    from pygui.qt.custom_widgets.toolbars import ToolBarCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


POINCARE_BUTTON_GROUP = "poincare_button_group"


class PoincareToolBarWidget(ToolBarCommon):
    """
    toolbar with some functionality specific to poincare plots
    """
    def __init__(self, parent=None, **params):
        super(PoincareToolBarWidget, self).__init__(parent,
                                    _check_groups=[POINCARE_BUTTON_GROUP],
                                    **params)


class ShowPoincareSettingsToolButton(ToolButtonType):
    """
    toolbar button to show poincar plot settings
    """
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [POINCARE_BUTTON_GROUP],
            'show_poincare_settings_handler', 'poincare_plot_settings',
            'Show poincare settings',
            'toolbar_show_poincare_settings_handler_callable')
        super(ShowPoincareSettingsToolButton, self).__init__(default, **params)
