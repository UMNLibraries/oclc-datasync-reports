# coding: utf-8
'''This script creates two files from the OCLC Datasync report file *xrefrept.txt:
1)a .txt. file of Alma MMS IDS formatted for input to Alma's set creation job; 
2) a file of brief MARC records from the OCLC Datasync report file *xrefrept.txt 
to be used as input for Alma import profile Add 035 (OCoLC)* numbers to existing records.
NOTE: At present, the outputs of this script must be processed by manually creating a set
and running two jobs via the Alma UI. An additional script is in development to execute 
these processes via API.'''

import csv
import pymarc
import os
import re
from datetime import date

def xref_rpt_parse(xreffile):
	today = str(date.today())
	
	f = open(xreffile, 'r')
	file = f.read()
	lines = file.split('\n')
	
	xref_parsed = []
	for line in lines:
			xref = line.split('\t')
			xref_parsed.append(xref)
		
	with open('upd_xref_' + today + '.mrc', 'wb') as processed, open('upd_mmsids_' + today + '.txt', 'w') as mmsid_file:
	
		rec_count = 0
		mmsid_file.write('MMS ID\n')

		for row in xref_parsed:
			brief_record = pymarc.Record(to_unicode=True, force_utf8=True)
			try:
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
			except IndexError:
				continue
			processed.write(brief_record.as_marc())
			mmsid_file.write(str(mmsid) + '\n')
			rec_count += 1
		
	return(rec_count)

def main():
	flist = [f for f in os.listdir() if re.match('.*[0-9]\\.xrefrpt.*', f)]
	if len(flist) != 1: 
		print('xrefrept file not found')
		fname = input('File to convert: ')
	else:
		fname = str(flist[0])
	count = xref_rpt_parse(fname)
	print('Done.', count, 'MARC records in file.')

if __name__=='__main__':
	main()