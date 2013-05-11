'''
Created on 11 maj 2013

@author: jurek
'''

import pylab as pl


def test_poincare(_file, _window_size):
    shift = 1
    _data = pl.loadtxt(_file, skiprows=1, usecols=[1, 2], unpack=True)
    signal = _data[0:1][0]
    signal_time = pl.sum(signal)
    #print(signal)
    annotation = _data[1:2][0]
    #print(annotation)
    index = 0
    suma_time = 0.0
    ca_time = 0.0
    cd_time = 0.0
    ca_count = 0
    cd_count = 0
    while (True):

        #if index + _window_size + shift <= len(signal):
        if index + _window_size + shift <= len(signal):
            indexes = pl.arange(index, index + _window_size)
            signal0 = signal.take(indexes)

            indexes_plus = pl.arange(index, index + _window_size - shift)
            signal0_plus = signal.take(indexes_plus)

            indexes_minus = pl.arange(index + shift, index + _window_size)
            signal0_minus = signal.take(indexes_minus)

            annotation0 = annotation.take(indexes)
            #print('*' * 50)
            #print('index: ' + str(index))
            #print('signal0: ' + str(signal0))
            #print('signal0_plus: ' + str(signal0_plus))
            #print('signal0_minus: ' + str(signal0_minus))
            #print('annotation0: ' + str(annotation0))
            signal0_time = pl.sum(signal0)
            suma_time = suma_time + signal0_time

            __sd1 = (signal0_plus - signal0_minus) / pl.sqrt(2)
            sd1 = pl.sqrt(pl.sum((__sd1 ** 2)) / len(signal0_plus))
            sd1d = pl.sqrt(pl.sum(__sd1[pl.find(__sd1 < 0)] ** 2) / len(signal0_plus)) # @IgnorePep8
            sd1a = pl.sqrt(pl.sum(__sd1[pl.find(__sd1 > 0)] ** 2) / len(signal0_plus)) # @IgnorePep8            
            #c1d = (sd1d / sd1) ** 2
            #c1a = (sd1a / sd1) ** 2

            #
            #
            __sd2 = (signal0_plus + signal0_minus) / pl.sqrt(2)
            #sd2 = pl.sqrt(pl.var(__sd2))

            #sd1 = (signal0_plus - signal0_minus) / pl.sqrt(2)
            nochange_indexes = pl.find(sd1 == 0)

            mean0_plus = pl.mean(signal0_plus)
            mean0_minus = pl.mean(signal0_minus)
            __sd2 = (signal0_plus - mean0_plus
                   + signal0_minus - mean0_minus) / pl.sqrt(2)
            sd2d = pl.sqrt((pl.sum(__sd2[pl.find(signal0_minus < signal0_plus)] ** 2)  # @IgnorePep8
                    + (pl.sum(__sd2[nochange_indexes] ** 2)) / 2) / pl.size(signal0_plus))  # @IgnorePep8

            sd2a = pl.sqrt((pl.sum(__sd2[pl.find(signal0_minus > signal0_plus)] ** 2)  # @IgnorePep8
                    + (pl.sum(__sd2[nochange_indexes] ** 2)) / 2) / pl.size(signal0_plus))  # @IgnorePep8            
            #c2d = (sd2d / sd2) ** 2
            #c2a = (sd2a / sd2) ** 2

            sdnna = pl.sqrt((sd1a ** 2 + sd2a ** 2) / 2)
            sdnnd = pl.sqrt((sd1d ** 2 + sd2d ** 2) / 2)
            sdnn = pl.sqrt(sdnna ** 2 + sdnnd ** 2)

            ca = (sdnna / sdnn) ** 2
            cd = (sdnnd / sdnn) ** 2
            #c = ca + cd
            if ca > cd:
                ca_count += 1
            else:
                cd_count += 1
            #print(type(c))
            #print("ca={0:20.10f} cd={1:20.10f} c={2:20.10f}".format(ca, cd, c)) # @IgnorePep8
            #if not c == 1.0:
            #    print('ERROR')
            #print(c)
            #print('c2d: ' + str(c2d))

            if ca > 0.5:
                ca_time = ca_time + signal0_time

            if cd > 0.5:
                cd_time = cd_time + signal0_time

            index += 1
        else:
            break

    #suma_time = signal_time
    return 'ca_summary_time: ' + str(ca_time / suma_time) + \
        ' cd_summary_time: ' + str(cd_time / suma_time) + \
        ' ca_count: ' + str(ca_count) + ' cd_count: ' + str(cd_count)

if __name__ == '__main__':
    #print('normal: ' + test_poincare("o:\\dane\\30m\\normal\\0029_.rea", 300))
    #print('shuffled: ' + test_poincare("o:\\dane\\30m\\shuffled\\S0029_.rea", 300)) # @IgnorePep8
    #print('normal: ' + test_poincare("o:\\dane\\30m\\normal\\0004.rea", 300))
    #print('shuffled: ' + test_poincare("o:\\dane\\30m\\shuffled\\S0004.rea", 300)) # @IgnorePep8

    katalog = "o:\\test_random_24h\\"
    pliki = [
        'ANDRZ29.rea',
        'ANDRZ30.rea',
        'bader_RR.rea',
        'BAJER9.rea',
        'bajolek_RR.rea',
        'BALCERAK.rea',
        'bieniek_RR.rea',
        'bucior_RR.rea',
        'chmiel_RR.rea',
        'CHUDO28.rea',
        'chybel_RR.rea',
        'chybow_RR.rea',
        'ciesla_RR.rea',
        'cisze_RR.rea',
        'CYFER12.rea',
        'CYRAN16.rea',
        'CYRAN17.rea',
        'drewn_RR.rea',
        'eob_RR.rea',
        ]

    for plik in pliki:
        print('plik: ' + plik)
        print('normal: ' + test_poincare(katalog + plik, 300))  # @IgnorePep8
        print('shuffled: ' + test_poincare(katalog + "S_" + plik, 300))  # @IgnorePep8    
