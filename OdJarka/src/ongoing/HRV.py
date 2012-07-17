from numpy import *
from scipy import where
from re import findall
from poincare import *

def read_data(reafile, columnRR, columnANNOT):
    """this function loads the data to the memory
    the imput variables are:
    reafile - the name of the file containing the data in the .rea format
    columnRR - the number of the column holding the RR time series
    columnANNOT - the number of the column holding the annotations

    the function returns:
    signal - the RR intervals
    annotations - the annotations
    """
    reafile_current=open(reafile, 'r')
    first_line=reafile_current.readline()
    signal=[] # this variable contains the signal for spectral analysis
    annotation=[]
    #here the reading of the file starts
    for line in reafile_current:
        line_content=findall(r'\b[0-9\.]+', line)
        signal.append(float(line_content[columnRR-1]))
        if columnRR!=columnANNOT:
            annotation.append(int(float(line_content[columnANNOT-1])))
    signal=array(signal)
    if columnRR==columnANNOT:
        annotation=0*signal
    annotation=array(annotation)
    reafile_current.close()
    return signal ,annotation

def filter_states():
    """This function defines the states of the filters used for filtering
    the RR intervals time series. It will return the following bool variables
    filtr_annot: logical variable, True is for <<use annotation filter>>
    filtr_square: logical variable, True is for <<use square filter>>
    filtr_quot: logical variable, True is for <<use quotient filter>>
    annot_leave: the annotations which will be left in the analysis (int array) - they will eventually be replaced by annotation 0
    up_bound: upper bound for the square filter (all values over this threshold will be annotated as 5)
    down_bound: lower bound for the square filter (all values under this threshold will be annotated as 5)
    percentage: the quotient between neighboring RRs which, when exceeded, will result in annotation 6
    """
    print """please select the type of filter you want to use
    1 annotation filter
    2 square filter
    3 quotient filter
    you can combine filters
    """
    filtr=raw_input('answer by giving the number corresponding to your filter e.g. 1 2 3: \n')
    filtr=findall(r'\b[0-9]+', filtr)
    filtr=array(map(int,filtr))

    #to powinno byc w funkcji zwracajacej filtry i ich wartosci
    annot_leave=[]
    up_bound=10000
    down_bound=0
    percentage=1000
    #koniec


    #teraz definiuje stan wybranych filtrow
    if len(where(filtr==1)[0])==1:
        filtr_annot=True
    else:
        filtr_annot=False
    if len(where(filtr==2)[0])==1:
        filtr_square=True
    else:
        filtr_square=False
    if len(where(filtr==3)[0])==1:
        filtr_quot=True
    else:
        filtr_quot=False

    #teraz uzytkownik wybierze parametry filtrow

    if filtr_annot==True:
        print "\n*** The annotation filter ***"
        print """The rea files contain the following annotations:
        0 -- sinus beat
        1 -- ventricular beat
        2 -- supraventricular beat
        3 -- artifact
        Enter a list of the beats you want TO LEAVE in the analysis
        (sinus beats will be left automatically, so you do not need to enter 0)"""
        annot_leave=raw_input()
        annot_leave=findall(r'\b[0-9]+', annot_leave)
        annot_leave=array(map(int,annot_leave))

    if filtr_square==True:
        print "\n*** The square filter ***"
        up_bound=float(raw_input('Enter the upper bound for the filter in ms (e.g. 2000): '))
        down_bound=float(raw_input('Enter the lower bound for the filter in ms (e.g. 300): '))

    else: up_bound=0; down_bound=0;

    if filtr_quot==True:
        print "\n*** The quotient filter ***"
        percentage=float(raw_input('Enter the percentage which disqualifies a beat \n(e.g. 30 means that a beat will be disqualified,\ni.e. will break any run, if it is greater or smaller\nthan the preceding beat by more than 30%: '))
    else: percentage=100;
    return_values= filtr_annot, filtr_square, filtr_quot, annot_leave, up_bound, down_bound, percentage
    return return_values
    
def filtrowanie(RR, anotacje, filtry_krotka):
    """this function finds the positions of the extra-sinus (or just unwanted) beats in the RR time series and replaces the corresponding annotations with number 5
    the input ariables are:
    RR:the time series of RR intervals (numpy array)
    anotacje: the annotations for each interval (numpy array)
    filtr_annot: logical variable, True is for <<use annotation filter>>
    filtr_square: logical variable, True is for <<use square filter>>
    filtr_quot: logical variable, True is for <<use quotient filter>>
    annot_leave: the annotations which will be left in the analysis (int array) - they will eventually be replaced by annotation 0
    up_bound: upper bound for the square filter (all values over this threshold will be annotated as 5)
    down_bound: lower bound for the square filter (all values under this threshold will be annotated as 5)
    percentage: the quotient between neighboring RRs which, when exceeded, will result in annotation 6

    this function returns:
    indeksy_do_wyrzucenia: indices of the undesirable beats (annotation different from 0)
    """

    filtr_annot=filtry_krotka[0]; filtr_square=filtry_krotka[1]; filtr_quot=filtry_krotka[2]; annot_leave=filtry_krotka[3]; up_bound=filtry_krotka[4]; down_bound=filtry_krotka[5];  percentage=filtry_krotka[6];

    if not filtr_annot:
        anotacje=anotacje*0
    if filtr_annot:
        for annot in annot_leave:
            indeksy_annot_leave=where(anotacje==annot)[0]
            anotacje[indeksy_annot_leave]=0
    if filtr_square:
        indeksy_up=where(RR>up_bound)[0]
        indeksy_down=where(RR<down_bound)[0]
        indeksy_square_up_down=r_[indeksy_down, indeksy_up]
        anotacje[indeksy_square_up_down]=5
    if filtr_quot:
        roznice=abs(diff(RR))
        reference=RR[1:]
        quota=roznice/reference
        indeksy_quota=where(quota*100>percentage)[0]+1
        anotacje[indeksy_quota]=6
    #tu zaczynam filtrowac dane, tzn. filtry przerywaja serie
    indeksy_do_wyrzucenia=array(where(anotacje!=0))[0]
    return indeksy_do_wyrzucenia

def runs_ultimate(RR, indeksy_do_wyrzucenia):
    """this function calculates the number of respective runs and calculates their positions

    the input variable are
    RR - the time series of RR intervals
    indeksy_do_wyrzucenia - the positions of the unwanted (e.g. extrasinus) beats which will break the runs

    the returned variables are:
    akumulator_up - a numpy array holding the number of runs of decelerations from 1 through 20 ("up" is from the position in the Poincare Plot)
    akumulator_down - a numpy array holding the number of runs of accelerations from 1 through 20 ("down" is from the position in the Poincare Plot)
    address_up - a structure (array of arrays) holding the exact positions of the END points of deceleration runs from 1 through 20
    address_down - a structure (array of arrays) holding the exact positions of the END points of accelerations runs from 1 through 20
    """
    znaki=diff(RR)
    znaki=sign(znaki)

    indeksy_do_wyrzucenia=r_[indeksy_do_wyrzucenia, indeksy_do_wyrzucenia-1]
    akumulator_down=arange(0,40)*0
    akumulator_up=arange(0,40)*0
    znaki[indeksy_do_wyrzucenia]=16
    
    index_up=0
    index_down=0

    flaga=znaki[0] #pamieta poprzedni znak

    #tu zdefiniujemy puste tablice, ktore beda pamietaly gdzie wypadaja konce serii
    address_up=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    address_down=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    #teraz zdefiniujemy odpowiednik numeru RR
    running_RR_number=1
    
    for znak in znaki[1:]:
        if flaga==1 and znak==1:
            index_up+=1
        if flaga==-1 and znak==-1:
            index_down+=1
        if flaga==1 and znak!=1:
            akumulator_up[index_up]+=1
            if index_up<20:
                address_up[index_up].append(running_RR_number)
            index_up=0
        if flaga==-1 and znak!=-1:
            akumulator_down[index_down]+=1
            if index_down<20:
                address_down[index_down].append(running_RR_number)
            index_down=0
        flaga=znak
        running_RR_number+=1

    if flaga==1 and znak==1:
        akumulator_up[index_up]+=1
        if index_up<20:
            address_up[index_up].append(running_RR_number)
    
    if flaga==-1 and znak==-1:
        akumulator_down[index_down]+=1
        if index_down<20:
            address_down[index_down].append(running_RR_number)

    return akumulator_up, akumulator_down, address_up, address_down

def runs_variance(RR, indeksy_do_wyrzucenia, address_up, address_down):
    """ this function calculates the parts of variance contributed by the respective runs of decelerations and accelerations

    the input variables are
    RR - the time series of RR intervals
    indeksy_do_wyrzucenia - the positions of the unwanted (e.g. extrasinus) beats
    address_up - a numpy structure holding the addresses of runs of decelerations of lengths 1 through 20 (up is from the position in the Poincare Plot)
    address_down - a numpy structure holding the addresses of runs of accelerations of lengths 1 through 20 (down is from the position in the Poincare Plot)

    the output variables are
    Var1_up - the parts of short term variance contributed by runs of decelerations of lengths 1 through 20
    Var1_down - the parts of short term variance contributed by runs of acceleration of lengths 1 through 20
    Var2_up - the parts of long term variance contributed by runs of decelerations of lengths 1 through 20
    Var2_down - the parts of long term variance contributed by runs of acceleration of lengths 1 through 20
    """
    
    anotacje=RR*0
    anotacje[indeksy_do_wyrzucenia]=5
    poincare_descripts=poincare(RR,anotacje,1)

    serie=arange(0,20)
    SSQ1_up=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    SSQ1_down=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    SSQ2_up=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    SSQ2_down=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    xcI=poincare_descripts[16]
    xcII=poincare_descripts[17]
    for seria_up in serie:
        if address_up[seria_up]!=[]:
            for index_seria_up in address_up[seria_up]:
                x_II=RR[index_seria_up-(seria_up):(index_seria_up+1)]
                x_I=RR[index_seria_up-(seria_up+1):(index_seria_up+1)-1]
                x1=(x_II-x_I)/sqrt(2)
                x2=(x_II-xcII+x_I-xcI)/sqrt(2)
                SSQ1_up[seria_up]+=sum(x1**2)
                SSQ2_up[seria_up]+=sum(x2**2)
    
    for seria_down in serie:
        if address_down[seria_down]!=[]:
            for index_seria_down in address_down[seria_down]:
                x_II=RR[index_seria_down-(seria_down):(index_seria_down+1)]
                x_I=RR[index_seria_down-(seria_down+1):(index_seria_down+1)-1]
                x1=(x_II-x_I)/sqrt(2)
                x2=(x_II-xcII+x_I-xcI)/sqrt(2)
                SSQ1_down[seria_down]+=sum(x1**2)
                SSQ2_down[seria_down]+=sum(x2**2)
    N_point=int32(poincare_descripts[14])
    Var1_up=SSQ1_up/N_point
    Var1_down=SSQ1_down/N_point
    Var2_up=SSQ2_up/N_point
    Var2_down=SSQ2_down/N_point

    return Var1_up, Var1_down, Var2_up, Var2_down
