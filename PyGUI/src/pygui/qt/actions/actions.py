'''
Created on 18-01-2013

@author: jurek
'''
from pygui.qt.utils.settings import SettingsFactory
from pygui.qt.utils.windows import AreYouSureWindow
from pygui.qt.utils.windows import InformationWindow


def clearSettings(dargs):
    parent = dargs.get('parent', None)
    if AreYouSureWindow(parent, title='Clearing settings'):
        SettingsFactory.clearSettings()
        InformationWindow(message="Settings cleared !")
