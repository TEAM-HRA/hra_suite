'''
Created on Jun 22, 2014

@author: jurek
'''

import glob
from scipy import *

lista_plikow=glob.glob('*.rea')

for plik in lista_plikow:
    dlugosc=0
    tekst=[]
    plik_rea=open(plik)
    for liniija in plik_rea:
        dlugosc=dlugosc+1
        tekst.append(liniija)
    indeksy=random.permutation(dlugosc-1)+1# + 1 zeby nie ruszac pierwszej linijki z nazwami kolumn
    nazwa_pliku='S'+plik[0:-4]+'.rea'
    shuffled_plik=open(nazwa_pliku, 'w')
    shuffled_plik.write(tekst[0])
    for i in arange(1, dlugosc):
        shuffled_plik.write(tekst[indeksy[i-1]])
    shuffled_plik.close()
    plik_rea.close()
