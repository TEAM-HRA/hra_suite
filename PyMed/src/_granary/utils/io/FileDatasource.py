'''
Created on 23-07-2012

@author: jurek
'''

import FileUtils
import collections

ColumnSpec = collections.namedtuple("ColumnSpec", "name coltype")


def getIndex(self, collection):
    for num, columnSpec in enumerate(collection):
        if columnSpec.name == self.name:
            return num
    return -1
ColumnSpec.getIndex = getIndex


#vv = ColumnSpec.keys();
#dd = dir(ColumnSpec)
#print(dd)

#s1 = ColumnSpec('aaa', 'bbb')
#s2 = ColumnSpec('cccc', 'dddd')
#l1 = [s1, s2]
#idx = s2.getIndex(l1)

class FileDatasource:

    def __init__(self, filename, columnsSpecs):
        self.__filename__ = filename
        self.__columnsSpecs__ = columnsSpecs
        self.__signal__ = None

    def getDataForColumn(self, columnName):
        if self.__signal__ is None:
            self.__loadFile__()
        return self.__signal__[self.__columnsSpecs__.index(columnName)]

    def __loadFile__(self):
        self.__signal__ = []
        for dummy in range(len(self.__columnsSpecs__)):  # create list of lists
            self.__signal__.append([])

        columns = FileUtils.getColumnNames(self.__filename__)

        dataFile = open(self.__filename__, 'r')
        dataFile.readline()  # skip first header line

        for line in dataFile:
            items = line.split()
            for columnSpec in self.__columnsSpecs__:
                value = float(items[columns.index(columnSpec.name)])
                if isinstance(columnSpec.coltype, int):
                    value = int(value)
                index = columnSpec.getIndex(self.__columnsSpecs__)
                (self.__signal__[index]).append(value)

        a = self.__signal__[0]
        b = self.__signal__[1]
        dataFile.close()

#'H:\\Dropbox\\Jurek_dzielone\\Dane30min\\0001.rea'
#time[min] rri[ms] rr-flags[] rr-systolic[mmHg] rr-diastolic[mmHg]rr-mean[mmHg]

filename = 'H:\\Dropbox\\Jurek_dzielone\\Dane30min\\0001.rea'
data = FileDatasource(filename, [ColumnSpec('rr-flags[]', int),
                                 ColumnSpec('rri[ms]', float)])
b1 = data.getDataForColumn('rr-flags[]')
h = 0
i = 0
i = i + 9
v1 = (i is None)
x1 = range(3)
