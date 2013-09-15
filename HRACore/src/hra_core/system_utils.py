'''
Created on Sep 15, 2013

@author: jurek
'''
import subprocess


def execute_command(command, lines_of_output=0):
    """
    execute command, returns outcome (in one a string object) depending on
    value of lines_of_output parameter:
    0 - no outcome
    -1 - all outcome
    <number> - number of lines of outcome
    """
    output = None
    for idx, _out in enumerate(run_command(command)):
        if idx < lines_of_output or lines_of_output == -1:
            if not output:
                output = ""
            output += _out
    return output


def run_command(command):
    """
    execute command, returns iterator over all outcomes
    """
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=True)
    return iter(p.stdout.readline, b'')
