import glob
import os.path as fs

summary_file_name = '/home/jurek/volumes/doctoral/dane/24h/output/summary.txt'
_path = '/home/jurek/volumes/doctoral/dane/24h/output/*.rea_sum'

summary_file_name = '/home/jurek/volumes/doctoral/dane/24h/output_stepper_300_bits/summary_300_bits.txt' # @IgnorePep8
_path = '/home/jurek/volumes/doctoral/dane/24h/output_stepper_300_bits/*.rea_sum' # @IgnorePep8
with open(summary_file_name, "w") as summary_file:
    first = True
    for _file in glob.glob(_path):
        with open(_file, "r") as _file:
            filename = fs.basename(_file.name).replace('_sum', '')
            print('Filename: ' + filename)
            headers = _file.readline()
            if first == True:
                summary_file.write('nazwa_pliku, ' + headers)
                first = False
            summary_file.write(filename + ', ' + _file.readline())
