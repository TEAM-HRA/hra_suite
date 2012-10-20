'''
Created on 20-10-2012

@author: jurek
'''
#!/usr/bin/env python

from os import system
import curses

from numpy import array
from pylab import find

from pycore.globals import DIR_DATA, EXT_MASK
from pymath.datasources import FilesDataSources, DataSource
from pymath.datasources import SignalColumnSpec
from pymath.datasources import AnnotationColumnSpec
from pymath.time_domain.poincare_plot.poincare_plot import PoincarePlot
from pymath.time_domain.poincare_plot.poincare_plot import PoincarePlotSegmenter #@IgnorePep8
from pymath.time_domain.poincare_plot.filters import RemoveAnnotatedSignalFilter #@IgnorePep8
from pymath.time_domain.poincare_plot.filters import ZeroAnnotationFilter
from pymath.time_domain.poincare_plot.filters import AnnotationShiftedPartsFilter #@IgnorePep8
from pymath.frequency_domain.fourier import FastFourierTransform


def get_param(prompt_string):
    screen.clear()
    screen.border(0)
    screen.addstr(2, 2, prompt_string)
    screen.refresh()
    input = screen.getstr(10, 10, 60)
    return input


def execute_cmd(cmd_string):
    system("clear")
    a = system(cmd_string)
    print ""
    if a == 0:
        print "Command executed correctly"
    else:
        print "Command terminated with error"
    raw_input("Press enter")
    print ""

x = 0

screen = curses.initscr()
while x != ord('4'):
    screen.clear()
    screen.border(0)
    screen.addstr(2, 2, "Please enter a number...")
    screen.addstr(4, 4, "1 - Add a user")
    screen.addstr(5, 4, "2 - Restart Apache")
    screen.addstr(6, 4, "3 - Show disk space")
    screen.addstr(7, 4, "4 - Exit")
    screen.addstr(8, 4, "Test")
    screen.refresh()

    x = screen.getch()

    if x == ord('1'):
        username = get_param("Enter the username")
        homedir = get_param("Enter the home directory, eg /home/nate")
        groups = get_param("Enter comma-separated groups, eg adm,dialout,cdrom") #@IgnorePep8
        shell = get_param("Enter the shell, eg /bin/bash:")
        curses.endwin()
        #execute_cmd("useradd -d " + homedir + " -g 1000 -G "
        #+ groups + " -m -s " + shell + " " + username)
    if x == ord('2'):
        curses.endwin()
        execute_cmd("df")
    if x == ord('3'):
        curses.endwin()
        execute_cmd("df -h")

curses.endwin()
