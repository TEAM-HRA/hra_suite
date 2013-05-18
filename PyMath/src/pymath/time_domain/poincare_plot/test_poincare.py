'''
Created on 11 maj 2013

@author: jurek
'''

import pylab as pl
import glob


def get_max_index_for_cumulative_sum_greater_then_value(_array, value,
                                                     start_index=0):
    """
    this function returns the first index of _array calculated from
    cumulative sum of values of _array where cumulative sum value is >= then
    passed value; searched indexes starts at start_index position
    """
    indexes = range(start_index, len(_array))
    sub_array = _array.take(indexes)
    cumulative_array = pl.cumsum(sub_array)
    indexes = pl.where(cumulative_array >= value)[0]
    return indexes[0] + start_index if len(indexes) > 0 else -1


def calculate(signal, rr_start, rr_stop, shift, suma_time, counter,
              ca_count, cd_count, equal_count, ca_time, cd_time):

    indexes = pl.arange(rr_start, rr_stop + 1)
    signal0 = signal.take(indexes)

    indexes_plus = pl.arange(rr_start, rr_stop + 1 - shift)
    signal0_plus = signal.take(indexes_plus)

    indexes_minus = pl.arange(rr_start + shift, rr_stop + 1)
    signal0_minus = signal.take(indexes_minus)
    #print(signal0_minus)

    signal0_time = pl.sum(signal0)
    suma_time = suma_time + signal0_time

    __sd1 = (signal0_plus - signal0_minus) / pl.sqrt(2)
    sd1 = pl.sqrt(pl.sum((__sd1 ** 2)) / len(__sd1))
    sd1_equal = pl.find(__sd1 == 0)
#            if len(sd1_equal) > 0:
#                print('sd1 equal: ' + str(sd1_equal))
    sd1d = pl.sqrt(pl.sum(__sd1[pl.find(__sd1 < 0)] ** 2) / len(__sd1)) # @IgnorePep8
    sd1a = pl.sqrt(pl.sum(__sd1[pl.find(__sd1 > 0)] ** 2) / len(__sd1)) # @IgnorePep8            
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
           + signal0_minus - mean0_minus
           ) / pl.sqrt(2)
    sd2d = pl.sqrt((pl.sum(__sd2[pl.find(signal0_minus < signal0_plus)] ** 2)  # @IgnorePep8
            + (pl.sum(__sd2[nochange_indexes] ** 2)) / 2
               ) / len(__sd2))  # @IgnorePep8

    sd2a = pl.sqrt((pl.sum(__sd2[pl.find(signal0_minus > signal0_plus)] ** 2)  # @IgnorePep8
            + (pl.sum(__sd2[nochange_indexes] ** 2)) / 2
                ) / len(__sd2))  # @IgnorePep8            
    #c2d = (sd2d / sd2) ** 2
    #c2a = (sd2a / sd2) ** 2

    sdnna = pl.sqrt((sd1a ** 2 + sd2a ** 2) / 2)
    sdnnd = pl.sqrt((sd1d ** 2 + sd2d ** 2) / 2)
    sdnn = pl.sqrt(sdnna ** 2 + sdnnd ** 2)

    ca = (sdnna / sdnn) ** 2
    cd = (sdnnd / sdnn) ** 2
    #print('ca: ' + str(ca) + ' cd: ' + str(cd) + ' ca + cd ' + str(ca+cd)) # @IgnorePep8
    #c = ca + cd
    counter += 1
    if ca > cd:
        ca_count += 1
    elif cd > ca:
        cd_count += 1
    else:
        equal_count += 1
    #print(type(c))
    #print("ca={0:20.10f} cd={1:20.10f} c={2:20.10f}".format(ca, cd, c)) # @IgnorePep8
    #if not c == 1.0:
    #    print('ERROR')
    #print(c)
    #print('c2d: ' + str(c2d))

    if ca > 0.5:
        ca_time = ca_time + signal0_time
    elif cd > 0.5:
        cd_time = cd_time + signal0_time
    else:
        ca_time = ca_time + signal0_time / 2
        cd_time = cd_time + signal0_time / 2

    return (counter, ca_count, cd_count, equal_count, ca_time, cd_time,
            suma_time)


def test_poincare_resampled(_file, _window_size, _cols=[1, 2],
                _dynamic_shift=None, step=10, count=1000):
    shift = 1
    _data = pl.loadtxt(_file, skiprows=1, usecols=_cols, unpack=True)
    signal = _data if len(_cols) == 1 else _data[0:1][0]
    signal_time = pl.sum(signal)

    sample = pl.arange(0, sum(signal), step)
    cumsum = pl.cumsum(signal)
    #print(annotation)
    index = 0
    suma_time = 0.0
    ca_time = 0.0
    cd_time = 0.0
    ca_count = 0
    cd_count = 0
    #while (True):
    #_size = len(signal0_plus)
    _size = step * count

    counter = 0
    equal_count = 0
    for i in range(len(sample) - count):

        rr_start = pl.searchsorted(cumsum, sample[i])
        #rr_stop = pl.searchsorted(cs, sample[i + count], side='left')
        rr_stop = pl.searchsorted(cumsum, sample[i + count])
        #if index + _window_size + shift <= len(signal):
        #if index + _window_size + shift <= len(signal):
        #if index + _window_size <= len(signal):
        if 1 == 1:
            #_size = rr_stop - rr_start + 1
            _size = count

            (counter, ca_count, cd_count,
             equal_count, ca_time, cd_time, suma_time) = \
                calculate(signal, rr_start, rr_stop, shift, suma_time, counter,
                      ca_count, cd_count, equal_count, ca_time, cd_time)

            index += 1
        else:
            break

    print('counter: ' + str(counter) + ' step: ' + str(step)
          + ' count: ' + str(count)
          + ' window size [in ms]: ' + str(step * count))

    #suma_time = signal_time
    return 'ca_summary_time: ' + str(ca_time / suma_time) + \
        ' cd_summary_time: ' + str(cd_time / suma_time) + \
        ' ca_count: ' + str(ca_count) + ' cd_count: ' + str(cd_count) + \
        ' equal_count: ' + str(equal_count) + ' counter: ' + str(counter) + '\n' # @IgnorePep8


def test_poincare_timed(_file, _window_size, _cols=[1, 2],
                _dynamic_shift=None, step=10, count=1000):
    shift = 1
    _data = pl.loadtxt(_file, skiprows=1, usecols=_cols, unpack=True)
    signal = _data if len(_cols) == 1 else _data[0:1][0]
    signal_time = pl.sum(signal)

    #print(annotation)
    suma_time = 0.0
    ca_time = 0.0
    cd_time = 0.0
    ca_count = 0
    cd_count = 0
    #while (True):
    #_size = len(signal0_plus)
    _size = step * count

    counter = 0
    equal_count = 0
    rr_start = 0
    while(True):

        rr_stop = get_max_index_for_cumulative_sum_greater_then_value(
                                            signal,
                                            _size,
                                            rr_start)
        if rr_stop == -1:
            break

        (counter, ca_count, cd_count,
         equal_count, ca_time, cd_time, suma_time) = \
            calculate(signal, rr_start, rr_stop, shift, suma_time, counter,
                  ca_count, cd_count, equal_count, ca_time, cd_time)

        rr_start += 1

    print('counter: ' + str(counter) + ' step: ' + str(step)
          + ' count: ' + str(count)
          + ' window size [in ms]: ' + str(step * count))
    #suma_time = signal_time
    return 'ca_summary_time: ' + str(ca_time / suma_time) + \
        ' cd_summary_time: ' + str(cd_time / suma_time) + \
        ' ca_count: ' + str(ca_count) + ' cd_count: ' + str(cd_count) + \
        ' equal_count: ' + str(equal_count) + ' counter: ' + str(counter) + '\n' # @IgnorePep8


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

    katalog = "o:\\test_regular\\"
    pliki = [
             "regular_even_small.rea"
             ]

    katalog = 'o:\\dane\\30m\\shuffled\\'
    pliki = [
             "S0009.rea"
             ]
    #'o:\\dane\\30m\\shuffled\\S0009.rea'

    test_poincare = test_poincare_timed

    katalog = "o:\\test_poincare\\"
    pliki = [
             "regular_even_0.rea",
             "regular_even_flawed.rea"
             ]

    titles = [
             "timed even: ",
             "timed flawed: "
             ]

    katalog = "o:\\test_poincare\\real\\shuffled_2"
    pliki = []
    titles = [
             "sampled shuffled: ",
             ]

    katalog = "o:\\dane\\30m\\normal"
    pliki = []
    titles = [
             "sampled shuffled: ",
             ]

    test_poincare = test_poincare_resampled

    if len(pliki) == 0:
        lista_plikow = glob.glob(katalog + '\\*.rea')
        pliki = [plik for plik in lista_plikow]
        titles = [titles[0] for _ in pliki]
        katalog = ""

    i = 0
    for plik in pliki:
        print('****************************************************')
        print('plik: ' + plik)
        print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=300, step=1000))  # @IgnorePep8
        print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=3000, step=100))  # @IgnorePep8
        #print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=30000, step=10))  # @IgnorePep8
        #print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=300000, step=1))  # @IgnorePep8
        #print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=1200, step=1000))  # @IgnorePep8
        print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=600, step=1000))  # @IgnorePep8
        print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=300, step=500))  # @IgnorePep8
        print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=111, step=700))  # @IgnorePep8
        print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=10, step=1000))  # @IgnorePep8
        print(titles[i] + test_poincare(katalog + plik, 18, [1,2], _dynamic_shift=3, count=10, step=500))  # @IgnorePep8
        i += 1
        #print('timed even: ' + test_poincare_timed(katalog + plik, 18, [0], _dynamic_shift=3, count=300, step=1000))  # @IgnorePep8        
        #print('shuffled: ' + test_poincare(katalog + "S_" + plik, 300))  # @IgnorePep8    
