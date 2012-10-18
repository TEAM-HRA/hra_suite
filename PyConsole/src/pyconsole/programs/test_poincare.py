'''
Created on 20-08-2012

@author: jurek
'''

from numpy import array
from pylab import find

from pycore.globals import DIR_DATA, EXT_MASK
from pymath.datasources import FilesDataSources, DataSource
from pymath.datasources import SignalColumnSpec
from pymath.datasources import AnnotationColumnSpec
from pymath.time_domain.poincare_plot.poincare_plot import PoincarePlot
from pymath.time_domain.poincare_plot.poincare_plot import PoincarePlotSegmenter #@IgnorePep8
from pymath.time_domain.poincare_plot.filters import RemoveAnnotatedSignalFilter #@IgnorePep8
from pymath.time_domain.poincare_plot.filters import ZeroAnnotationFilter
from pymath.time_domain.poincare_plot.filters import AnnotationShiftedPartsFilter #@IgnorePep8
from pymath.frequency_domain.fourier import FastFourierTransform


#s = [
#     750.625000,
#     756.250000,
#     731.250000,
#     745.625000,
#     781.875000,
#     778.125000,
#     741.875000,
#     761.875000,
#     773.750000,
#     775.000000,
#     757.500000
#]
#
#d = [
#    0.000000,
#    0.000000,
#    0.000000,
#    2.000000,
#    0.000000,
#    0.000000,
#    2.000000,
#    0.000000,
#    0.000000,
#    0.000000,
#    0.000000
#     ]
#
#s = array(s)
#d = array(d)
#
#data = DataSource(s, d)
#
#fff = FastFourierTransform(data)
#print(fff.calculate())
#
#out = PoincarePlot(data).statistics
#print('pp 1')
#print(out)
#
#out = PoincarePlot(AnnotationShiftedPartsFilter(data).filter).statistics
#print('pp 2 (filtered)')
#print(out)
#
#sdata = StatisticsFactory(
#                     (MeanStatistic, SDRRStatistic,
#                      NtotStatistic, TotTimeStatistic),
#                      data)
#print('statistics:')
#print(sdata.statistics)
#
#
#sdata = StatisticsFactory(
#                     (MeanStatistic, SDRRStatistic,
#                      NtotStatistic, TotTimeStatistic),
#                      RemoveAnnotatedSignalFilter(data).filter)
#print('filtered statistics:')
#print(sdata.statistics)

#sciezka = 'o:\\dane\\'
#ext = '*.rea'

#sys.path.append(sciezka)
#print('V1')
#with FilesDataSources(path=sciezka, ext=ext) as fs:
#    for _file in fs:
#        print(_file.name)
#
#
#print('V2')
#for _file in FilesDataSources(path=sciezka, ext=ext):
#    print(_file.name)


def test_data_source():

    annotation = [1, 0, 0, 0, 0, 1, 2, 1, 0, 2, 2]
    signal = [
            750.625000,
            756.250000,
            731.250000,
            745.625000,
            781.875000,
            778.125000,
            741.875000,
            761.875000,
            773.750000,
            775.000000,
            757.500000
    ]

    return DataSource(array(signal), array(annotation))


def test_poincare():
    print('DIR_DATA=' + str(DIR_DATA) + ' EXT_MASK=' + str(EXT_MASK))
    fd = FilesDataSources(path=DIR_DATA, ext=EXT_MASK)
    fd.setColumnsSpecs(SignalColumnSpec('rri[ms]'),
                       AnnotationColumnSpec('rr-flags[]'))
    print(fd.headers)

#    ddd = test_data_source()
#    fd = (ddd,)

    for d in fd:
        print(1)
        print(d)
        #2017
        for sub_d in PoincarePlotSegmenter(d, len(d.signal) - 1):
            print(2)
            print(sub_d)
            d2 = ZeroAnnotationFilter(sub_d, (1,)).filter
            print(3)
            print(d2)
    #        sdata = StatisticsFactory(
    #                             (MeanStatistic, SDRRStatistic,
    #                              NtotStatistic, TotTimeStatistic),
    #                              RemoveAnnotatedSignalFilter(d2).filter)
    #        print(sdata.statistics)
            print(4)
            print(RemoveAnnotatedSignalFilter(d2).filter.statistics)

            anno = AnnotationShiftedPartsFilter(d2).filter
            print(anno)

            pp = PoincarePlot(anno).statistics
            print(pp)

            ff = FastFourierTransform(d2).interpolation_linear.calculate
            print(5)
            print(ff)

            #print(PoincarePlot(sub_d).statistics)
            #print(" ".join([str(len(sub_d.data.take(range(3)))),
            #str(sub_d.data.take(range(3)))]))


def test_array():
    _annotation = array([0, 1, 0, 0, 0, 1, 2, 1])

    leave_annotations = [1]
    for pobudzenie in leave_annotations:
        index_pobudzenie = find(_annotation == pobudzenie)
        index_pobudzenie = array(index_pobudzenie)
        count = sum(index_pobudzenie != 0)
        if count:
            _annotation[index_pobudzenie] = 0
        x = 0
        x += 1

#test_array()
test_poincare()
