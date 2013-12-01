'''
Created on Nov 25, 2013

@author: jurek
'''

import numpy as np

#columns:
stats = {"mean": 0, "sd": 1, "median": 2, "min": 3, "max": 4}

#rows:
params = {"SD1": 0, "SD2": 1, "SDNN": 2, "SD1d": 3,
        "SD1a": 4, "SD2d": 5, "SD2a": 6, "SDNNd": 7, "SDNNa": 8}
data = np.array(
            [[24.02, 11.94, 19.96, 9.61, 72.91],
            [187.37, 52.41, 182.42, 94.25, 347.29],
            [133.70, 37.56, 129.48, 67.29, 247.81],
            [17.59, 9.18, 15.03, 7.01, 55.36],
            [16.32, 7.71, 13.95, 6.57, 47.45],
            [130.53, 35.73, 127.72, 65.47, 234.88],
            [134.38, 38.47, 130.37, 67.80, 255.81],
            [93.25, 25.68, 91.32, 46.76, 167.99],
            [95.79, 27.49, 93.20, 48.38, 182.18]])


def _v(data, stat, param):
    row = params.get(param)
    column = stats.get(stat)
    #print ('stat: ' + stat + ' param: ' + param + ' row: ' + str(row) +
    #       ' column: ' + str(column) + ' value: ' + str(data[row][column]))
    return data[row, column]


def calculate_asymmetyry(data, stat):
    C1d = (_v(data, stat, "SD1d") ** 2) / (_v(data, stat, "SD1") ** 2)
    C1a = (_v(data, stat, "SD1a") ** 2) / (_v(data, stat, "SD1") ** 2)

    C2d = (_v(data, stat, "SD2d") ** 2) / (_v(data, stat, "SD2") ** 2)
    C2a = (_v(data, stat, "SD2a") ** 2) / (_v(data, stat, "SD2") ** 2)

    Cd = (_v(data, stat, "SDNNd") ** 2) / (_v(data, stat, "SDNN") ** 2)
    Ca = (_v(data, stat, "SDNNa") ** 2) / (_v(data, stat, "SDNN") ** 2)

    print('For ' + stat)
    print('Short term: C1d > C1a => ' + str(C1d) + " " + str(C1a)
           + " => " + str(C1d > C1a))
    print('Long term:  C2a > C2d => ' + str(C2a) + " " + str(C2d)
           + " => " + str(C2a > C2d))
    print('Total:      Ca > Cd   => ' + str(Ca) + " " + str(Cd)
          + " => " + str(Ca > Cd))
    print('')
for stat in stats:
    calculate_asymmetyry(data, stat)
