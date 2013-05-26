'''
Created on 18-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from pygui.qt.utils.settings import SettingsFactory
    from pygui.qt.utils.settings import DEFAULT_SETTINGS_GROUP
    from pygui.qt.utils.windows import AreYouSureWindow
    from pygui.qt.utils.windows import InformationWindow
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.signals import CLEAR_ACTIVITIES_SIGNAL
    from pygui.qt.utils.signals import EXIT_APPLICATION_SIGNAL
except ImportError as error:
    ImportErrorMessage(error, __name__)


def clearSettings(dargs):
    parent = dargs.get('parent', None)
    if AreYouSureWindow(parent, title='Clearing settings'):
        SettingsFactory.clearSettings(DEFAULT_SETTINGS_GROUP)
        InformationWindow(message="Settings cleared !")


def clearActivities(dargs):
    parent = dargs.get('parent', None)
    if AreYouSureWindow(parent, title='Clearing activities'):
        SignalDispatcher.broadcastSignal(CLEAR_ACTIVITIES_SIGNAL)
        InformationWindow(message="Activities cleared !")


def exitApplication(dargs):
    parent = dargs.get('parent', None)
    if AreYouSureWindow(parent, title='Exit application ?'):
        SignalDispatcher.broadcastSignal(EXIT_APPLICATION_SIGNAL)
