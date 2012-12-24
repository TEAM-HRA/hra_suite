'''
Created on 24-12-2012

@author: jurek
'''


def ImportErrorMessage(importError):
    """
    method which dynamically show Tk window
    with import message error
    """
    code = """\
from Tkinter import *
root = Tk()
message = '""" + importError.message + """\\n' + \\
         'Check if it is a hidden import during build process'
w = Label(root, text=message)
w.pack()
root.mainloop()
"""
    exec(code)
