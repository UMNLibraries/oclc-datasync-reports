# oclc-datasync
OCLC Datasync processing scripts. These scripts process OCLC-generated reports from 
Datasync set holdings jobs and produce a holdings delete report for submission to OCLC
Datasync.

## datasync_xref_update.py
This script updates OCLC numbers in Alma bibliographic records based on the OCLC
Datasync cross-reference report *xrefrpt.txt. Based on that file, the script fetches
each record via the Alma bib API, adds or changes the OCLC number in the MARCXML record, 
and replaces the Alma bib record with the updated record. It can be used instead of the 
datasync_xref.py script, which produces files for manual Alma jobs that accomplish the same
thing.

## datasync_unres_analytics.py
This script requires as input the OCLC Datasync unresolved report file *unresxrefrpt.txt. Based on
that file, the script creates a CSV from the text file, creates an Alma Analytics filter of Alma MMS IDs 
from the list in the unresolved report, pulls an XML report via the Alma Analytics API using that filter, 
parses that XML report, and creates one Excel file for each UMMBL OCLC symbol for human review and processing.
It automates a bunch of stuff that must be done manually if using datasync_unres.py and can be used instead of
that script.

## datasync_exception_report.py
This script turns the OCLC Datasync exceptions report file bibdetailexcpt.txt 
into something more useful for subsequent manual processing (Excel). The .txt file
is parsed based on the content of each error message, and output is written to an Excel
Workbook with two worksheets: one for MARC errors unrelated to non-Latin scripts, 
and one for MARC errors apparently related to non-Latin scripts.

## datasync_delete_report.py
This script fetches predefined deleted holdings reports from Alma Analytics
for each OCLC symbol managed under UMMBL (MNU, MND, MCR, MNX, MLL), parses the reports, 
and outputs a CSV file for the OCLC Datasync process.

### Other scripts

The two other scripts in this repo produce files for manual processing in Alma and Alma Analytics.
The scripts above are better/more automated options, but these can be used if more hands-on processing
is preferred:

## dataysnc_xref.py
This script creates two files from the OCLC Datasync report file *xrefrpt.txt:
1)a .txt. file of Alma MMS IDS formatted for input to Alma's set creation job; 
2) a file of brief MARC records from the OCLC Datasync report file *xrefrpt.txt 
to be used as input for Alma import profile Add 035 (OCoLC)* numbers to existing records.
The outputs of this script must be processed by manually creating a set
and running two jobs via the Alma UI. Another script in this repo, datasync_xref_update.py,
processes the xrefrpt file and updates Alma bib records via API. It can be used instead of
this script.

## datasync_unres.py
This script produces an .xlsx file and a .txt file for each of the 5 University of Minnesota
OCLC symbols (MNU, MLL, MND, MNX, MCR. Files are to be used for manual processing of records 
returned as unresolved by OCLC Datasync. Inputs required: OCLC Datasync unresolved 
cross-ref report, One .csv file per symbol from Alma Analytics (e.g. 'OCLC Datasync 
Unresolved processing MNU'). Another script in this repo, datasync_unres_analytics.py, eliminates
the necessity to pull the Analytics reports manually and can be used instead.

This work is copyright (c) the Regents of the University of Minnesota, 2017. It was created by Stacie Traill and last updated 2019-05-08.
