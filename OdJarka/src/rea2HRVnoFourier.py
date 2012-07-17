#imports
import sys
dysk=raw_input("where is the Python24 folder? enter the disc letter (e.g. C or D): \n")
sciezka=dysk+':\\Python24\\lib\\site-packages\\HRV\\'
sys.path.append(sciezka)

from re import *
from glob import *
from scipy import *
from poincare import *
from fourierHRV import *
from read_data import *
from matplotlib.mlab import *

#ten kawalek utworzy liste plikow, odczyta pierwsza linijke pierwszego pliku z listy
#i przy jej pomocy stworzy menu czytajace nazwy kolumn - potem uzytkownik wybierze
#kolumny i gites
print "\nI can see the following columns in the .rea files: \n"
lista_plikow=glob('*.rea')
file_rea=open(lista_plikow[0], 'r')
pierwsza=file_rea.readline()
nazwy_kolumn=findall(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]+', pierwsza)
index=1
nazwy_kolumn=nazwy_kolumn[1:]
for nazwa in nazwy_kolumn:
    print index, nazwa
    index=index+1
print ' '
wybrane_kolumny=raw_input(" Enter the number of the column you want to analyze and the number of the annotation column e.g. '1 2'. If you do not have the annotation column write 0 instead, e.g. 1 0\n\n")
kolumny=findall(r'\b[0-9]+', wybrane_kolumny)
kolumna=int(kolumny[0])
anotacje=int(kolumny[1])
if anotacje==0:
    anotacje=kolumna;
file_rea.close()

rodzaj_transformaty=0

print """What kind of filtering would you like to apply to Poincare plot calculations:
(0) no filtering (1) annotation filtering (2) ratio filtering (3) square filtering?"""
filtering=int(raw_input())
if filtering==1:
    print """there are the following annotations used: 0-normal beat
    1 - ventricular beat, 2 - supraventricular beat, 3 - artifact
    choose the beats you want TO LEAVE in the analysis, e.g. if you
    want to remove the artefacts and ventricular beats but leave
    the supraventricular beats you should enter 2
    """
    leave_annotations=raw_input()
    leave_annotations=findall(r'\b[0-9]+', leave_annotations)
    leave_annotations=map(int, leave_annotations)
print "Thank you!"

#po zamnknieciu pierwszego pliku (patrz wyzej) ponizsza petla iteruje od nowa przez
#cala liste plikow
file_result=open('results.csv','w')
file_result.write('name,mean,SDRR,RMSSD,SD1,SD2,SD21,S,R,SD1up,SD1down,asym,Nup,Ndown,Non,N, totTime,VLF,LF,HF, LFnu, HFnu, TP0.5, TP0.4, LF/HF, ln(LF), ln(HF), ln(TP0.5), ln(TP0.4)\n')
for plik in lista_plikow:
    
    signal, annotation=read_data(plik, kolumna+1, anotacje+1 )
    if filtering==1:
        for pobudzenie in leave_annotations:
            index_pobudzenie=find(annotation==pobudzenie)
            index_pobudzenie=array(index_pobudzenie)
            if sum(index_pobudzenie!=0):
                annotation[index_pobudzenie]=0
    #obliczamy wyniki
    RR_mean, sdrr,rmssd,sd1,sd2,sd21,s,r,sd1up,sd1down,asym,nup,ndown,non,ntot,tot_time=poincare(signal, annotation, filtering)
    #if rodzaj_transformaty==1:
    #    print "niestety na razie nie ma lomba - zrobie zwykle fft"
    #    rodzaj_transformaty=2
    #if rodzaj_transformaty==2:
    #    moc=fourierHRV(signal, annotation,rodzaj_transformaty-1)
    #LF=moc[0][0]
    #HF=moc[0][1]
    #TP0_5=moc[0][2]
    #TP0_4=moc[0][3]
    #VLF=moc[0][4]
    #LFnu=(LF/(TP0_4-VLF))*100
    #HFnu=(HF/(TP0_4-VLF))*100
    file_result.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d,%f\n"% (plik, RR_mean,sdrr,rmssd,sd1,sd2,sd21,s,r,sd1up,sd1down,asym,nup,ndown,non,ntot,tot_time))

file_result.close()
print "zrrrrrrobione!!! - press [ENTER]"
raw_input();
