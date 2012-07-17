from scipy import *
from re import *
def read_data(reafile, columnRR, columnANNOT):
    print "read data"
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
    return signal ,annotation
    
