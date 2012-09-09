'''
Created on 18-07-2012

@author: jurek
'''

from pylab import diff
from pylab import sign
from pylab import arange
from pylab import r_
from pylab import sqrt
from pylab import int32

from _granary.math.poincare.Poincare import Poincare


class DataSeries(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    @staticmethod
    def runs_ultimate(RR, indeksy_do_wyrzucenia):
        """this function calculates the number of respective runs and
        calculates their positions
        the input variable are
        RR - the time series of RR intervals
        indeksy_do_wyrzucenia - the positions of the unwanted (e.g. extrasinus)
        beats which will break the runs
        the returned variables are:
        akumulator_up - a numpy array holding the number of runs of
        decelerations from 1 through 20 ("up" is from the position in
        the Poincare Plot)
        akumulator_down - a numpy array holding the number of runs of
        accelerations from 1 through 20 ("down" is from the position in
        the Poincare Plot) address_up - a structure (array of arrays)
        holding the exact positions of the END points of deceleration runs
        from 1 through 20
        address_down - a structure (array of arrays) holding the exact
        positions of the END points of accelerations runs from 1 through 20
        """
        znaki = diff(RR)
        znaki = sign(znaki)

        indeksy_do_wyrzucenia = r_[indeksy_do_wyrzucenia,
                                   indeksy_do_wyrzucenia - 1]
        akumulator_down = arange(0, 40) * 0
        akumulator_up = arange(0, 40) * 0
        znaki[indeksy_do_wyrzucenia] = 16

        index_up = 0
        index_down = 0

        flaga = znaki[0]  # pamieta poprzedni znak

        #tu zdefiniujemy puste tablice, ktore beda pamietaly gdzie
        #wypadaja konce serii
        address_up = [[], [], [], [], [], [], [], [], [], [], [], [], [], [],
                      [], [], [], [], [], []]
        address_down = [[], [], [], [], [], [], [], [], [], [], [], [], [], [],
                        [], [], [], [], [], []]
        #teraz zdefiniujemy odpowiednik numeru RR
        running_RR_number = 1

        for znak in znaki[1:]:
            if flaga == 1 and znak == 1:
                index_up += 1
            if flaga == -1 and znak == -1:
                index_down += 1
            if flaga == 1 and znak != 1:
                akumulator_up[index_up] += 1
                if index_up < 20:
                    address_up[index_up].append(running_RR_number)
                index_up = 0
            if flaga == -1 and znak != -1:
                akumulator_down[index_down] += 1
                if index_down < 20:
                    address_down[index_down].append(running_RR_number)
                index_down = 0
            flaga = znak
            running_RR_number += 1

        if flaga == 1 and znak == 1:
            akumulator_up[index_up] += 1
            if index_up < 20:
                address_up[index_up].append(running_RR_number)

        if flaga == -1 and znak == -1:
            akumulator_down[index_down] += 1
            if index_down < 20:
                address_down[index_down].append(running_RR_number)

        return akumulator_up, akumulator_down, address_up, address_down

    @staticmethod
    def runs_variance(RR, indeksy_do_wyrzucenia, address_up, address_down):
        """ this function calculates the parts of variance contributed by
        the respective runs of decelerations and accelerations

        the input variables are
        RR - the time series of RR intervals
        indeksy_do_wyrzucenia - the positions of the unwanted (e.g. extrasinus)
        beats address_up - a numpy structure holding the addresses of
        runs of decelerations of lengths 1 through 20 (up is from
        the position in the Poincare Plot) address_down - a numpy structure
        holding the addresses of runs of accelerations of lengths 1 through 20
        (down is from the position in the Poincare Plot)

        the output variables are
        Var1_up - the parts of short term variance contributed by
        runs of decelerations of lengths 1 through 20 Var1_down - the parts of
        short term variance contributed by runs of acceleration of lengths
        1 through 20 Var2_up - the parts of long term variance contributed
        by runs of decelerations of lengths 1 through 20
        Var2_down - the parts of long term variance contributed
        by runs of acceleration of lengths 1 through 20
        """

        anotacje = RR * 0
        anotacje[indeksy_do_wyrzucenia] = 5
        poincare_descripts = Poincare.poincare(RR, anotacje, 1)

        serie = arange(0, 20)
        SSQ1_up = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        SSQ1_down = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                     ]
        SSQ2_up = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        SSQ2_down = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                     ]
        xcI = poincare_descripts[16]
        xcII = poincare_descripts[17]
        for seria_up in serie:
            if address_up[seria_up] != []:
                for index_seria_up in address_up[seria_up]:
                    x_II = RR[index_seria_up - (seria_up):(index_seria_up + 1)]
                    x_I = RR[index_seria_up
                             - (seria_up + 1):(index_seria_up + 1) - 1]
                    x1 = (x_II - x_I) / sqrt(2)
                    x2 = (x_II - xcII + x_I - xcI) / sqrt(2)
                    SSQ1_up[seria_up] += sum(x1 ** 2)
                    SSQ2_up[seria_up] += sum(x2 ** 2)

        for seria_down in serie:
            if address_down[seria_down] != []:
                for index_seria_down in address_down[seria_down]:
                    x_II = RR[index_seria_down -
                              (seria_down):(index_seria_down + 1)]
                    x_I = RR[index_seria_down
                             - (seria_down + 1):(index_seria_down + 1) - 1]
                    x1 = (x_II - x_I) / sqrt(2)
                    x2 = (x_II - xcII + x_I - xcI) / sqrt(2)
                    SSQ1_down[seria_down] += sum(x1 ** 2)
                    SSQ2_down[seria_down] += sum(x2 ** 2)
        N_point = int32(poincare_descripts[14])
        Var1_up = SSQ1_up / N_point
        Var1_down = SSQ1_down / N_point
        Var2_up = SSQ2_up / N_point
        Var2_down = SSQ2_down / N_point

        return Var1_up, Var1_down, Var2_up, Var2_down
