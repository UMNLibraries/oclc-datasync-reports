# oclc-datasync
OCLC Datasync processing scripts. These scripts take as input the 3 report files generated
by an OCLC Datasync job: *xrefrpt.txt, *unresxrefrpt.txt, and *bibdetailexcpt.txt. Outputs
are files to be used for either batch or manual processing of Datasync results in Alma.

## dataysnc_xref.py
This script creates two files from the OCLC Datasync report file \*xrefrept.txt:
1)a .txt. file of Alma MMS IDS formatted for input to Alma's set creation job; 
2) a file of brief MARC records to be used as input for Alma import profile 
Add 035 (OCoLC)* numbers to existing records.

## datasync_unres.py
This script produces an .xlsx file and a .txt file for each of the 5 University of Minnesota
OCLC symbols. Files are to be used for manual processing of records returned as unresolved by
OCLC Datasync. Inputs required: OCLC Datasync unresolved cross-ref report, One .csv file per
symbol from Alma Analytics (e.g. 'OCLC Datasync Unresolved processing MNU').

## datasync_exception_report.py
This script parses the OCLC Datasync report file \*bibdetailexcpt.txt, and writes to an Excel
Workbook with two worksheets: one for MARC errors unrelated to non-Latin scripts, and one for MARC
errors apparently related to non-Latin scripts.
