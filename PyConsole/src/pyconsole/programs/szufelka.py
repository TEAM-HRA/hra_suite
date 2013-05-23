import glob
import time
import sys
#from scipy import *
from numpy import random
from numpy.core.numeric import arange


def process_file(plik, plik_out=None, counter=None):
    dlugosc = 0
    tekst = []
    plik_rea = open(plik)
    for liniija in plik_rea:
        dlugosc = dlugosc + 1
        tekst.append(liniija)
    # + 1 zeby nie ruszac pierwszej linijki z nazwami kolumn
    indeksy = random.permutation(dlugosc - 1) + 1

    _plik = plik[0:-4]
    if plik_out:
        _plik = plik_out
    if counter:
        _plik = _plik + "_" + str(counter)
    nazwa_pliku = 'S_' + _plik + '.rea'
    print('Process file: ' + plik + ' Output file: ' + nazwa_pliku)

    shuffled_plik = open(nazwa_pliku, 'w')
    shuffled_plik.write(tekst[0])
    for i in arange(1, dlugosc):
        shuffled_plik.write(tekst[indeksy[i - 1]])
    shuffled_plik.close()
    plik_rea.close()
    time.sleep(2)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        process_file(sys.argv[1])
    elif len(sys.argv) == 3:
        process_file(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        for i in range(1, int(sys.argv[3])):
            process_file(sys.argv[1], sys.argv[2], i)
    else:
        lista_plikow = glob.glob('*.rea')

        for plik in lista_plikow:
            process_file(plik)
