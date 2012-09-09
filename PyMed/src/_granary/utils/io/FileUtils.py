'''
Created on 18-07-2012

@author: jurek
'''

from re import findall
from numpy import array


def getColumnNames(filename):
    dataFile = open(filename, 'r')
    firstLine = dataFile.readline()
    columnNames = findall(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]+', firstLine)
    dataFile.close()
    return columnNames


class FileUtils(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
    @staticmethod
    def read_data(reafile, columnRR, columnANNOT):
        """this function loads the data to the memory
        the imput variables are:
        reafile - the name of the file containing the data in the .rea format
        columnRR - the number of the column holding the RR time series
        columnANNOT - the number of the column holding the annotations

        the function returns:
        signal - the RR intervals
        annotations - the annotations
        """
        reafile_current = open(reafile, 'r')
        first_line = reafile_current.readline()
        signal = []  # this variable contains the signal for spectral analysis
        annotation = []
        #here the reading of the file starts
        for line in reafile_current:
            line_content = findall(r'\b[0-9\.]+', line)
            signal.append(float(line_content[columnRR - 1]))
            if columnRR != columnANNOT:
                annotation.append(int(float(line_content[columnANNOT - 1])))
        signal = array(signal)
        if columnRR == columnANNOT:
            annotation = 0 * signal
        annotation = array(annotation)
        reafile_current.close()
        return signal, annotation
