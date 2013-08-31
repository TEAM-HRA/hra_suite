'''
Created on 6 maj 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from hra_gui.qt.custom_widgets.toolbars import ToolBarCommon
    from hra_gui.qt.custom_widgets.toolbars import ToolButtonType
    from hra_gui.qt.custom_widgets.toolbars import DefaultToolButtonType
except ImportError as error:
    ImportErrorMessage(error, __name__)


POINCARE_BUTTON_GROUP = "poincare_button_group"


class PoincareToolBarWidget(ToolBarCommon):
    """
    toolbar with some functionality specific to poincare plots
    """
    def __init__(self, parent=None, **params):
        excluded_buttons = None if params.get('reload_button', False) \
                            else [ReloadPoincareSettingsToolButton]
        super(PoincareToolBarWidget, self).__init__(parent,
                                    _check_groups=[POINCARE_BUTTON_GROUP],
                                    excluded_buttons=excluded_buttons,
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


class ReloadPoincareSettingsToolButton(ToolButtonType):
    """
    toolbar button to reload poincare plot settings
    """
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [POINCARE_BUTTON_GROUP],
            'reload_poincare_settings_handler',
            'reload_poincare_plot_settings',
            'Reload poincare settings',
            'toolbar_reload_poincare_settings_handler_callable')
        super(ReloadPoincareSettingsToolButton, self).__init__(default,
                                                               **params)


class ShowPoincareMovieToolButton(ToolButtonType):
    """
    toolbar button to show poincar plot movie settings
    """
    def __init__(self, **params):
        default = DefaultToolButtonType(True, [POINCARE_BUTTON_GROUP],
            'show_poincare_movie_handler', 'poincare_plot_movie',
            'Show poincare movie',
            'toolbar_show_poincare_movie_handler_callable')
        super(ShowPoincareMovieToolButton, self).__init__(default, **params)
