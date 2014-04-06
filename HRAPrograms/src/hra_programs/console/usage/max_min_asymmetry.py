'''
Created on Mar 29, 2014

@author: jurek
'''

import glob
import numpy as np

path = '/home/jurek/volumes/doctoral/doktorat_wyniki/long_24h_corrected_5m_stepper/*.rea_out'

#SD1 ; SD2 ; SD2SD1 ; Ss ; C1a ; SDNNa ; SDNNd ; C1d ; SD1Asymmet; CountBelow; C2a ; C2d ;
# CS ; SD2dSD1d ; CountAbove; Cd ; SD2aSD1a ; C1d50C2d50; SD2Asymmet; SDNN; SD2a; SD2d; SD1d; SD1a; SD21; Ca
c1d_col_number = 7
c2d_col_number = 11
usecols = []
usecols.append(c1d_col_number)
usecols.append(c2d_col_number)

v = []
for file_ in glob.glob(path):
    #print 'file: ', file_

    c1d, c2d = np.loadtxt(file_,
         skiprows=1, delimiter=';', usecols=usecols,
         unpack=True)
    #c1d_elements = c1d - 0.5
    sd1_5 = np.sum(np.power(c1d - 0.5, 2))
    sd2_5 = np.sum(np.power(c2d - 0.5, 2))

    sd1_5 = np.sqrt(np.sum(np.power(c1d - 0.5, 2))) / len(c1d) * 1000
    sd2_5 = np.sqrt(np.sum(np.power(c2d - 0.5, 2))) / len(c2d) * 1000

    v.append((file_, sd1_5, sd2_5, sd1_5 + sd2_5))

dtype = [('file', 'S100'), ('sd1_5', float), ('sd2_5', float), ('sd_sum', float)]
values = np.array(v, dtype=dtype)
sorted_values = np.sort(values, order='sd_sum')
for (file_, sd1_5_v, sd2_5_v, sd_sum_v) in sorted_values:
    print 'file: ', file_, ' sd_sum: ', sd_sum_v, ' sd1_5: ', sd1_5_v, ' sd2_5: ', sd2_5_v

