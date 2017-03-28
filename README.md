# oclc-datasync
OCLC Datasync processing scripts

## datasync_unres.py
This script produces an .xlsx file and a .txt file for each of the 5 University of Minnesota
OCLC symbols. Files are to be used for manual processing of records returned as unresolved by
OCLC Datasync. Inputs required: OCLC Datasync unresolved cross-ref report, One .csv file per
symbol from Alma Analytics (e.g. 'OCLC Datasync Unresolved processing MNU').

## datasync_exception_report.py
This script parses the OCLC Datasync report file *bibdetailexcpt.txt, and writes to an Excel
Workbook with two worksheets: one for MARC errors unrelated to non-Latin scripts, and one for MARC
errors apparently related to non-Latin scripts.
