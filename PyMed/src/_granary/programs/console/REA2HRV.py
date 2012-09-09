'''
Created on 18-07-2012

@author: jurek
'''

if __name__ == '__main__':
    pass


#imports
import sys
#J.E. dysk=raw_input("where is the Python24 folder?
#enter the disc letter (e.g. C or D): \n")
#J.E sciezka=dysk+':\\Python24\\lib\\site-packages\\HRV\\'
#sciezka='H:\\Dropbox\\Jurek_dzielone\\Dane30min\\'
sciezka = 'o:\\dane\\'
sys.path.append(sciezka)

print sys.path

from re import *
from glob import *
from scipy import *

#from fourierHRV import *
#from read_data import *
from matplotlib.mlab import *

from _granary.math.poincare.Poincare import Poincare
from _granary.utils.io.FileUtils import FileUtils
from _granary.math.series.Fourier import Fourier

from numpy import *

x1 = array([[1, 2], [3, 4]])

#ten kawalek utworzy liste plikow, odczyta pierwsza
#linijke pierwszego pliku z listy
#i przy jej pomocy stworzy menu czytajace nazwy kolumn -
#potem uzytkownik wybierze
#kolumny i gites
print "\nI can see the following columns in the .rea files: \n"
lista_plikow = glob(sciezka + '*.rea')
file_rea = open(lista_plikow[0], 'r')
pierwsza = file_rea.readline()
nazwy_kolumn = findall(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]+', pierwsza)
index = 1
nazwy_kolumn = nazwy_kolumn[1:]
for nazwa in nazwy_kolumn:
    print index, nazwa
    index = index + 1
print ' '
# wybrane_kolumny = raw_input(" Enter the number of the column you want to "
#  + "analyze and the number of the annotation column e.g. '1 2'."
#  + " If you do not have the annotation column write 0 instead, e.g. 1 0\n\n")

wybrane_kolumny = "1 2"
kolumny = findall(r'\b[0-9]+', wybrane_kolumny)
kolumna = int(kolumny[0])
anotacje = int(kolumny[1])
if anotacje == 0:
    anotacje = kolumna
file_rea.close()
print """Chose the kind of Fourier Transform:
(0) no FFT (1) Lomb (highly recommended)  (2)"
+" FFT interpolated (3) FFT imputated"""
#rodzaj_transformaty = int(raw_input())
rodzaj_transformaty = 2

print """What kind of filtering would you like to apply to
Poincare plot calculations:
(0) no filtering (1) annotation filtering (2) ratio
 filtering (3) square filtering?"""
#filtering = int(raw_input())
filtering = 1
if filtering == 1:
    print """there are the following annotations used: 0-normal beat
    1 - ventricular beat, 2 - supraventricular beat, 3 - artifact
    choose the beats you want TO LEAVE in the analysis, e.g. if you
    want to remove the artefacts and ventricular beats but leave
    the supraventricular beats you should enter 2
    """
    leave_annotations = "0"#raw_input()
    leave_annotations = findall(r'\b[0-9]+', leave_annotations)
    leave_annotations = map(int, leave_annotations)
print "Thank you!"

#po zamnknieciu pierwszego pliku (patrz wyzej) ponizsza petla iteruje
#od nowa przez cala liste plikow
file_result = open('results.csv', 'w')
file_result.write('name,mean,SDRR,RMSSD,SD1,SD2,SD21,S,R,SD1up,SD1down,' +
'asym,Nup,Ndown,Non,N, totTime,VLF,LF,HF, LFnu, HFnu, TP0.5, TP0.4,' +
'LF/HF, ln(LF),ln(HF), ln(TP0.5), ln(TP0.4)\n')
for plik in lista_plikow:

    signal, annotation = FileUtils.read_data(plik, kolumna + 1, anotacje + 1)
    if filtering == 1:
        #implemented as med.time_domain.poincare_plot.filters.ClearAnnotationFilter
        for pobudzenie in leave_annotations:
            index_pobudzenie = find(annotation == pobudzenie)
            index_pobudzenie = array(index_pobudzenie)
            if sum(index_pobudzenie != 0):
                annotation[index_pobudzenie] = 0
    print ('size: ' + str(len(signal)))
    #obliczamy wyniki
    (RR_mean, sdrr, rmssd, sd1, sd2, sd21, s, r, sd1up, sd1down,
        asym, nup, ndown, non, ntot, tot_time) = Poincare.poincare(signal,
                                                annotation, filtering)
    if rodzaj_transformaty == 1:
        print "niestety na razie nie ma lomba - zrobie zwykle fft"
        rodzaj_transformaty = 2
    if rodzaj_transformaty == 2:
        moc = Fourier.fourierHRV(signal, annotation, rodzaj_transformaty - 1)
    if rodzaj_transformaty != 0:
        LF = moc[0][0]
        HF = moc[0][1]
        TP0_5 = moc[0][2]
        TP0_4 = moc[0][3]
        VLF = moc[0][4]
        LFnu = (LF / (TP0_4 - VLF)) * 100
        HFnu = (HF / (TP0_4 - VLF)) * 100
#        file_result.write(("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d,%f," +
#                          "%f,%f,%f,%f,%f,%f\n")
#                          %
#                          (plik, RR_mean, sdrr, rmssd, sd1, sd2, sd21, s,
#                           r, sd1up, sd1down, asym, nup, ndown, non, ntot,
#                           tot_time, VLF, LF, HF, LFnu, HFnu, TP0_5)
#                          )

        file_result.write(("%s,%f,%f,%f,%f,%f,%f,%f" +
                          ",%f,%f,%f,%d,%d,%d, T %d T,%d" +
                          ",%f,%f,%f,%f,%f,%f,%f" +
                          ",%f,%f,%f,%f" +
                          ",%f,%f" +
                          "\n")
                          %
                          (plik, RR_mean, sdrr, rmssd, sd1, sd2, sd21, s
                           , r, sd1up, sd1down, asym, nup, ndown, non, ntot
                           , tot_time, VLF, LF, HF, LFnu, HFnu, TP0_5
                           , TP0_4, LF / HF, log(LF), log(HF)
                           , log(TP0_5), log(TP0_4)
                           )
                          )
    else:
        file_result.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d," +
                          "%f\n" % (plik, RR_mean, sdrr, rmssd, sd1, sd2,
                                     sd21, s, r, sd1up, sd1down, asym,
                                     nup, ndown, non, ntot, tot_time))

file_result.close()
print "zrrrrrrobione!!! - press [ENTER]"
raw_input()
