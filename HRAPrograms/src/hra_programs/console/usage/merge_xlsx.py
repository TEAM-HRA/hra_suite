'''
Created on Jan 3, 2014

@author: jurek
'''
import argparse
from openpyxl import Workbook
from openpyxl import load_workbook
import glob
from hra_core.io_utils import get_first_lines
from hra_core.io_utils import get_filename
#from hra_core.io_utils import get_dirname
from hra_core.misc import extract_number

# example of eclipse parameters:
#-source_xls '/home/jurek/tmp/klinika.xlsx'
#-source_csv_files_mask '/home/jurek/volumes/doctoral/monitor_do_impedancji_niccomo_wyniki/SVR_team/*.res_out'  # @IgnorePep8
#-separator ';'

parser = argparse.ArgumentParser()
parser.add_argument("-source_xls", "--source_xls", help="source xls file")
parser.add_argument("-source_csv_files_mask", "--source_csv_files_mask",
                    help="source csv files list mask")
parser.add_argument("-separator", "--separator", help="separator")
__args = parser.parse_args()


def merge_xls(source_xls, source_csv_files_mask, separator):
    #output_xls = "%s/%s_out.xlsx" % (get_dirname(source_xls),
    #                                 get_filename(source_xls))

    xls = None
    merged_sheet = None
    for file_nr, _file in enumerate(glob.glob(source_csv_files_mask)):
        #if file_nr == 2:
        #    break
        print('*****************************')
        print('Processing file: ' + str(_file))
        if xls == None:
            xls = load_workbook(source_xls)
            merged_sheet = xls.get_sheet_by_name('merged')
            lp_cells = merged_sheet.columns[0]
            headers_cells = merged_sheet.rows[0]

        (headers_line, values_line) = get_first_lines(_file, count=2)
        filename = get_filename(_file)
        (group, file_ident) = filename.split('_')
        headers = [str(group + "_" + header.strip())
                        for header in headers_line.split(separator)]
        values = [value.strip() for value in values_line.split(separator)]

        file_number = extract_number(file_ident)
        ident_row = None
        for cell in lp_cells:
            if file_number == cell.value:
                ident_row = cell.row - 1
                break

        #print("ident_row: " + str(ident_row))
        #add header
        save = False
        if ident_row:
            for header_idx, header in enumerate(headers):

                ident_column = None
                for cell in headers_cells:
                    if header == cell.value:
                        ident_column = cell.column
                        break
                if ident_column == None:
                    ident_column = merged_sheet.get_highest_column()
                    header_cell = merged_sheet.cell(row=0, column=ident_column)
                    header_cell.value = header
                    value_cell = merged_sheet.cell(row=ident_row,
                                               column=ident_column)
                    save = True
                else:
                    value_cell = merged_sheet.cell(
                                coordinate=ident_column + str(ident_row + 1))
                value_cell.value = values[header_idx]
        else:
            print('No item in xls file for ' + str(_file))
            return
        if save:
            print("Saving " + source_xls)
            xls.save(source_xls)
            xls = None

    if not xls == None:
        print("Saving " + source_xls)
        xls.save(source_xls)


merge_xls(__args.source_xls, __args.source_csv_files_mask, __args.separator)

print('The End')
