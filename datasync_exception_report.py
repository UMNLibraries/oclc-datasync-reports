# coding: utf-8
'''This script turns the OCLC Datasync exceptions report file bibdetailexcpt.txt 
into something more useful for subsequent manual processing (Excel). The .txt file
is parsed based on the content of each error message, and output is written to an Excel
Workbook with two worksheets: one for MARC errors unrelated to non-Latin scripts, 
and one for MARC errors apparently related to non-Latin scripts.'''

import os
import re
from openpyxl import Workbook
from datetime import date

def excpt_rpt_parse(excptfile):
    f = open(excptfile, 'r')
    file = f.read()
    flines = file.split('\n')
    lines = flines[6:]

    bibexcpt_parsed = []
    for line in lines:
        bibexcpt = line.split('\t')
        bibexcpt_parsed.append(bibexcpt)

    script_errors = [['Alma OCN', 'Staging OCN', 'MMS ID', 'Exception Count', 'Exception Description', 'Severity']]
    other_errors = [['Alma OCN', 'Staging OCN', 'MMS ID', 'Exception Count', 'Exception Description', 'Severity']]

    for line in bibexcpt_parsed:
        if re.match('^.*\s880(\s|\.).*$', str(line)) is not None:
            script_errors.append(line)
        elif re.match('^.*\$6.*$', str(line)) is not None:
            script_errors.append(line)
        else:
            other_errors.append(line)

    today = str(date.today())
    wb = Workbook()
    with open('oclc_datasync_errors_' + today + '.xlsx', 'wb') as excel_out:
        ws1 = wb.active
        ws1.title = 'other errors'
        for row in other_errors:
            ws1.append(row)
    
        ws2 = wb.create_sheet(title='script errors')
        for row in script_errors:
            ws2.append(row)
        
        wb.save(excel_out)

def main():
    flist = [f for f in os.listdir() if re.match('.*bibdetailexcpt.*', f)]
    if len(flist) != 1:
        excptfile = input('bibdetailexcpt file not found. Please enter Exceptions filename: ')
    else:
        excptfile = str(flist[0])
    excpt_rpt_parse(excptfile)
    print('Exceptions report generated successfully.')


if __name__=='__main__':
    main()