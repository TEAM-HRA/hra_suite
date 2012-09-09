'''
Created on 18-07-2012

@author: jurek
'''

from re import findall
from pylab import find
from pylab import array
from pylab import arange
from pylab import r_
from pylab import where
from pylab import diff


class Filter(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    @staticmethod
    def filter(signal, annotation):
        indexy = find(annotation == 0)
        indexy = array(indexy)
        signal = signal[indexy]
        return signal

    @staticmethod
    def pfilter(signal, annotation):
        #wykrywanie i usuwanie nonsinus na poczatku i na koncu
        while annotation[0] != 0:
            signal = signal[1:-1]
            annotation = annotation[1:-1]
        #removing nonsinus beats from the end
        while annotation[-1] != 0:
            signal = signal[0:-2]
            annotation = annotation[0:-2]
        indexy_p = array(find(annotation != 0))
        indexy_m = indexy_p - 1
        indexy = r_[indexy_p, indexy_m]
        x_p = signal[arange(0, len(signal) - 1)]
        x_pp = signal[arange(1, len(signal))]
        x_p[indexy] = -1
        indexy = array(find(x_p != -1))
        x_p = x_p[indexy]
        x_pp = x_pp[indexy]
        return x_p, x_pp

    @staticmethod
    def filter_states():
        """This function defines the states of the filters used for filtering
        the RR intervals time series. It will return the following bool
        variables
        filtr_annot: logical variable, True is for <<use annotation filter>>
        filtr_square: logical variable, True is for <<use square filter>>
        filtr_quot: logical variable, True is for <<use quotient filter>>
        annot_leave: the annotations which will be left in the analysis
        (int array) - they will eventually be replaced by annotation 0
        up_bound: upper bound for the square filter (all values over this
        threshold will be annotated as 5)
        down_bound: lower bound for the square filter (all values under this
        threshold will be annotated as 5)
        percentage: the quotient between neighboring RRs which, when exceeded,
        will result in annotation 6
        """
        print """please select the type of filter you want to use
        1 annotation filter
        2 square filter
        3 quotient filter
        you can combine filters
        """
        filtr = raw_input('answer by giving the number' +
                          ' corresponding to your filter e.g. 1 2 3: \n')
        filtr = findall(r'\b[0-9]+', filtr)
        filtr = array(map(int, filtr))

        #to powinno byc w funkcji zwracajacej filtry i ich wartosci
        annot_leave = []
        up_bound = 10000
        down_bound = 0
        percentage = 1000
        #koniec

        #teraz definiuje stan wybranych filtrow
        if len(where(filtr == 1)[0]) == 1:
            filtr_annot = True
        else:
            filtr_annot = False
        if len(where(filtr == 2)[0]) == 1:
            filtr_square = True
        else:
            filtr_square = False
        if len(where(filtr == 3)[0]) == 1:
            filtr_quot = True
        else:
            filtr_quot = False

        #teraz uzytkownik wybierze parametry filtrow

        if filtr_annot == True:
            print "\n*** The annotation filter ***"
            print """The rea files contain the following annotations:
            0 -- sinus beat
            1 -- ventricular beat
            2 -- supraventricular beat
            3 -- artifact
            Enter a list of the beats you want TO LEAVE in the analysis
            (sinus beats will be left automatically, so you do not
            need to enter 0)"""
            annot_leave = raw_input()
            annot_leave = findall(r'\b[0-9]+', annot_leave)
            annot_leave = array(map(int, annot_leave))

        if filtr_square == True:
            print "\n*** The square filter ***"
            up_bound = float(raw_input('Enter the upper bound for the filter' +
                                       ' in ms (e.g. 2000): '))
            down_bound = float(raw_input('Enter the lower bound for the filter'
                                    + ' in ms (e.g. 300): '))

        else:
            up_bound = 0
            down_bound = 0

        if filtr_quot == True:
            print "\n*** The quotient filter ***"
            percentage = float(raw_input('Enter the percentage which ' +
            'disqualifies a beat \n(e.g. 30 means that a beat will be ' +
            'disqualified,\ni.e. will break any run, if it is greater ' +
            'or smaller\nthan the preceding beat by more than 30%: '))
        else:
            percentage = 100
        return_values = (filtr_annot, filtr_square, filtr_quot,
                         annot_leave, up_bound, down_bound, percentage)
        return return_values

    @staticmethod
    def filtrowanie(RR, anotacje, filtry_krotka):
        """this function finds the positions of the extra-sinus
        (or just unwanted) beats in the RR time series and replaces
        the corresponding annotations with number 5
        the input ariables are:
        RR:the time series of RR intervals (numpy array)
        anotacje: the annotations for each interval (numpy array)
        filtr_annot: logical variable, True is for <<use annotation filter>>
        filtr_square: logical variable, True is for <<use square filter>>
        filtr_quot: logical variable, True is for <<use quotient filter>>
        annot_leave: the annotations which will be left in the analysis
        (int array) - they will eventually be replaced by annotation 0
        up_bound: upper bound for the square filter (all values over this
        threshold will be annotated as 5)
        down_bound: lower bound for the square filter (all values under
        this threshold will be annotated as 5)
        percentage: the quotient between neighboring RRs which, when exceeded,
        will result in annotation 6

        this function returns:
        indeksy_do_wyrzucenia: indices of the undesirable beats
        (annotation different from 0)
        """

        filtr_annot = filtry_krotka[0]
        filtr_square = filtry_krotka[1]
        filtr_quot = filtry_krotka[2]
        annot_leave = filtry_krotka[3]
        up_bound = filtry_krotka[4]
        down_bound = filtry_krotka[5]
        percentage = filtry_krotka[6]

        if not filtr_annot:
            anotacje = anotacje * 0
        if filtr_annot:
            for annot in annot_leave:
                indeksy_annot_leave = where(anotacje == annot)[0]
                anotacje[indeksy_annot_leave] = 0
        if filtr_square:
            indeksy_up = where(RR > up_bound)[0]
            indeksy_down = where(RR < down_bound)[0]
            indeksy_square_up_down = r_[indeksy_down, indeksy_up]
            anotacje[indeksy_square_up_down] = 5
        if filtr_quot:
            roznice = abs(diff(RR))
            reference = RR[1:]
            quota = roznice / reference
            indeksy_quota = where(quota * 100 > percentage)[0] + 1
            anotacje[indeksy_quota] = 6
        #tu zaczynam filtrowac dane, tzn. filtry przerywaja serie
        indeksy_do_wyrzucenia = array(where(anotacje != 0))[0]
        return indeksy_do_wyrzucenia
