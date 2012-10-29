'''
Created on 21-10-2012

@author: jurek
'''

import os
from pycore.globals import GLOBALS
from pycore.io_utils import expand_files
import subprocess


print('PROGRAM_PATH: ' + GLOBALS.PROGRAM_DIR)
print('MENUS_FILE: ' + GLOBALS.MENUS_FILE)
print('PLUGINS_DIR: ' + GLOBALS.PLUGINS_DIR)

print(expand_files(GLOBALS.PLUGINS_DIR, "egg", as_string=True))

add_paths = [
            "H:\\workspaces\\all\\doctorate\\PyConsole\\src\\",
            "H:\\python\\python_64\\Python27",
            "H:\\python\\python_64\\Python27\\DLLs",
            "H:\\python\\python_64\\Python27\\lib",
            "H:\\python\\python_64\\Python27\\lib\\plat-win",
            "H:\\python\\python_64\\Python27\\lib\\lib-tk",
            "H:\\python\\python_64\\Python27\\lib\\site-packages",
            "."
            ]

PATH = os.environ['PATH']
_env = {}
_env['PYTHONPATH'] = expand_files(GLOBALS.PLUGINS_DIR, "egg", as_string=True) + ";" + ";".join(add_paths) #@IgnorePep8
print('PYTHONPATH: ' + str(_env['PYTHONPATH']))
_env['PATH'] = PATH + ";h:\\python\\python_64\\Python27;H:\\python\\python_64\\Python27\\Scripts" #@IgnorePep8
args = ['cmd', '/K', 'start', 'python',
        'main_curses_med.py']
#errorlog = open("H:\\temp\\errorlog.log", 'w')
p = subprocess.Popen(" ".join(args), shell=True, env=_env,
                    #stdout=subprocess.PIPE,
                    creationflags=0x08000000  # subprocess.STDOUT,
                    #stderr=subprocess.STDOUT  # subprocess.STDOUT
                    #stderr=subprocess.STDOUT
                    #stdout=subprocess.STDOUT,
                    )
#, bufsize=100, shell=True, env=_env)
#stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print('TYPE: ' + str(type(p.stdout)))

#retval = p.wait()
#for line in p.stdout:  # .stderr.readlines():
#    print line,
#errorlog.close()
