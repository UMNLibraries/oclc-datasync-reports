# coding: utf-8
'''This script parses the OCLC Datasync report file bibdetailexcpt.txt, and writes to an Excel
Workbook with two worksheets: one for MARC errors unrelated to non-Latin scripts, and one for MARC
errors apparently related to non-Latin scripts.'''

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
    other_errors = script_errors

    for line in bibexcpt_parsed:
        if re.search(r'^.*\s880(\s|\.).*$', str(line)) is None and re.search(r'^.*\$6.*$', str(line)) is None:
            other_errors.append(line)
        else:
            script_errors.append(line)

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
    excptfile = input('Exceptions filename: ')
    excpt_rpt_parse(excptfile)
    print('Exceptions report generated successfully.')


if __name__=='__main__':
    main()