'''
Created on 04-11-2012

@author: jurek
'''
#!/usr/bin/python ~workspace/pyqt/dialogs/main.py

from PyQt4 import QtGui

#-------------------------------------------------------
# create the wizard classes


class MoviesPage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(MoviesPage, self).__init__(parent)
        self.setTitle('Movies')
        self.setSubTitle('Setup movie specific data')


class FramesPage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(FramesPage, self).__init__(parent)
        self.setTitle('Frames')
        self.setSubTitle('Setup frame specific data')


class RenderSettingsPage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(RenderSettingsPage, self).__init__(parent)
        self.setTitle('Render Settings')
        self.setSubTitle('Setup common render settings for all types')

#-------------------------------------------------------
# create the dialog class


class OptionsDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(OptionsDialog, self).__init__(parent)
        self.setWindowTitle('Options')

#-------------------------------------------------------
# create the main window class


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ApplicationWindow, self).__init__(parent)
        self.setWindowTitle('Main Window')

        # tie together the different settngs through the main menu
        file_menu = self.menuBar().addMenu('File')
        action = file_menu.addAction('Export Movies...')
        action.triggered.connect(self.exportMovies)
        action = file_menu.addAction('Export Frames...')
        action.triggered.connect(self.exportFrames)

        options_menu = self.menuBar().addMenu('Options')
        action = options_menu.addAction('Edit Preferences')
        action.triggered.connect(self.editPreferences)

    def exportMovies(self):
        """ Launches the export movies wizard. """
        wizard = QtGui.QWizard(self)
        wizard.addPage(MoviesPage(wizard))
        wizard.addPage(RenderSettingsPage(wizard))
        wizard.exec_()

    def exportFrames(self):
        """ Launches the export frames wizard. """
        wizard = QtGui.QWizard(self)
        wizard.addPage(FramesPage(wizard))
        wizard.addPage(RenderSettingsPage(wizard))
        wizard.exec_()

    def editPreferences(self):
        """ Launches the edit preferences dialog for this window. """
        dlg = OptionsDialog(self)
        dlg.exec_()

if (__name__ == '__main__'):
    # create the application if necessary
    app = None
    if (not QtGui.QApplication.instance()):
        app = QtGui.QApplication([])

    window = ApplicationWindow()
    window.show()

    # execute the application if we've created it
    if (app):
        app.exec_()
