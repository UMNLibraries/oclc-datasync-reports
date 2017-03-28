# coding: utf-8
'''This script creates brief MARC records from the OCLC Datasync report file
*xrefrept.txt to be used as input for Alma import profile "Add 035 (OCoLC)* numbers to existing records."'''

import csv
import pymarc
import os
from datetime import date

def xref_rpt_parse(xreffile):
    f = open(xreffile, 'r')
    file = f.read()
    lines = file.split('\n')

    xref_parsed = []
    for line in lines:
        xref = line.split('\t')
        xref_parsed.append(xref)
        
    with open('upd_xref_out.mrc', 'wb') as processed:
		rec_count = 0
    	for row in xref_parsed:

            brief_record = pymarc.Record(to_unicode=True, force_utf8=True)

            mmsid = row[0]
            newocn = row[1]

            field_001 = pymarc.Field(tag='001', data=mmsid)
            field_035 = pymarc.Field(
                    tag = '035',
                    indicators = [' ',' '],
                    subfields = ['a', '(OCoLC)' + newocn]
                    )
            field_245 = pymarc.Field(
                    tag = '245',
                    indicators = [' ',' '],
                    subfields = ['a', 'Title']
                    )
            brief_record.add_ordered_field(field_001)
            brief_record.add_ordered_field(field_035)
            brief_record.add_ordered_field(field_245)

            processed.write(brief_record.as_marc())
            rec_count += 1

    return(rec_count)

def main():
        fname = input('File to convert: ')
        count = xref_rept_parsed(fname)
        print('Done.', count, 'MARC records in file.')

if __name__=='__main__':
    main()