'''
This script produces an .xlsx file and a .txt file for each of the 5 University of Minnesota
OCLC symbols (MNU, MLL, MND, MNX, MCR. Files are to be used for manual processing of records 
returned as unresolved by OCLC Datasync. Inputs required: OCLC Datasync unresolved 
cross-ref report, One .csv file per symbol from Alma Analytics (e.g. 'OCLC Datasync 
Unresolved processing MNU'). NOTE: At present, the .csv files must be created within the Alma 
Analytics UI and manually downloaded to the working directory; an additional script is in 
development that will pull the Alma Analytics data via API.
'''

import csv
import re
import os
import petl as etl
from datetime import date
#also requires openpyxl, xlrd, xlwt


def unresrept_parse(unresfile):
    f = open(unresfile, 'r')
    file = f.read()
    flines = file.split('\n')
    unres_parsed = [['MMS ID', 'Staging OCN']]
    
    for line in flines:
        xref = line.split('\t')
        if xref is not None:
            unres_parsed.append(xref)
        
    with open('unresxref.csv', 'w', newline='') as out:
              writer = csv.writer(out)
              writer.writerows(unres_parsed)    


def xref_symbol_reports():
    symbol_reports = [f for f in os.listdir() if re.match('OCLC Datasync Unresolved.*\.csv', f)]
    
    today = str(date.today())
    
    for report in symbol_reports:
        
        symbol_split = re.split('^.*processing.(M[A-Z]{2}).*$', report)
        symbol = symbol_split[1]
        xlsx_outfile = symbol + '_datasync_unresolved_' + today + '.xlsx'
        xls_outfile = symbol + '_datasync_unresolved_' + today + '.xls'
        txt_outfile = symbol + '_staging_OCNs_' + today + '.txt'
        
        symbol_table_raw = etl.fromcsv(report, encoding='utf-8')
        symbol_table = etl.rename(symbol_table_raw, '\ufeffMMS Id', 'MMS ID')
        symbol_table2 = etl.select(symbol_table, "{MMS ID} is not None")
        symbol_table_sorted = etl.sort(symbol_table2, 'MMS ID')
        
        xref_table = etl.fromcsv('unresxref.csv')
        xref_table2 = etl.select(xref_table, "{MMS ID} is not None")
        xref_table_sorted = etl.sort(xref_table2, 'MMS ID')
        
        
        symbol_xref_table = etl.join(symbol_table_sorted, xref_table_sorted, presorted=True, lkey="MMS ID", rkey="MMS ID")
        
        try:
            etl.toxlsx(symbol_xref_table, xlsx_outfile, encoding='utf-8')
        except TypeError:
            etl.toxls(symbol_xref_table, xls_outfile, 'Sheet1', encoding='utf-8')
        
        staging_ocns_table = etl.cut(symbol_xref_table, 'Staging OCN')
        template = '{Staging OCN}\n'
        etl.totext(staging_ocns_table, txt_outfile, template=template)


def main():
    oclc_report_files = [f for f in os.listdir() if re.match('.*unresxrefrpt.*', f)]
    if len(oclc_report_files) != 1:
    	unresfile = input('unresxrefrpt file not found. Please supply filename: ')
    else:
    	unresfile = str(oclc_report_files[0])
    print('Parsing unresxrefrpt file...')
    unresrept_parse(unresfile)
    print('Building reports for each OCLC symbol...')
    xref_symbol_reports()
    print('Done')

if __name__=='__main__':
    main()