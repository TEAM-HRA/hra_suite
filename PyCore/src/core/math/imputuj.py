#from scipy import *
#from pylab import *
#
#'''
#moved to med.time_domain.poincare_plot.filters.MeanAnnotationFilter
#'''
#def imputuj(signal, annotation):
#    sinus_index = find(annotation == 0)
#    nonsinus_index = find(annotation != 0)
#    mean_sinus = mean(signal[sinus_index])
#    signal[nonsinus_index] = mean_sinus
#    return signal
