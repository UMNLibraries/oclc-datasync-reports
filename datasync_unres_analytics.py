'''This script requires as input the OCLC Datasync unresolved report file *unresxrefrpt.txt. Based on
that file, the script creates a CSV from the text file, creates an Alma Analytics filter of Alma MMS IDs 
from the list in the unresolved report, pulls an XML report via the Alma Analytics API using that filter, 
parses that XML report, and creates one Excel file for each UMMBL OCLC symbol for human review and processing.'''

import csv
import re
import os
import requests
import pyaml
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from lxml import etree
from datetime import date
from copy import deepcopy


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


def build_report_filter():

    filter_prefix = '<sawx:expr xsi:type="sawx:comparison" op="in" xmlns:saw="com.siebel.analytics.web/report/v1.1" xmlns:sawx="com.siebel.analytics.web/expression/v1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><sawx:expr xsi:type="sawx:sqlExpression">"Bibliographic Details"."MMS Id"</sawx:expr>'
    filter_suffix = '</sawx:expr>'
    with open('unresxref.csv') as unresxref:
        reader = csv.reader(unresxref)
        mmsids = []
        try:
            for row in reader:
                if str(row[0]).startswith('9'):
                    mmsids.append(row[0])
        except:
            IndexError
            next
    filter_list = []
    for m in mmsids:
        mmsid = str(m)
        filter_exp = '<sawx:expr xsi:type="xsd:string">' + mmsid + '</sawx:expr>'
        filter_list.append(filter_exp)
    filter_mmsids = ''.join(filter_list)
    mmsid_filter = filter_prefix + filter_mmsids + filter_suffix
    return mmsid_filter


def get_apikey():

    config = pyaml.yaml.load(open('config.yml'))
    apikey = config.get('apikey')
    return apikey

def get_analytics_report(mmsid_filter, apikey):

    url_root = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    path = '/shared/University of Minnesota/Twin Cities/OCLC Datasync/OCLC Datasync Unresolved processing ALL SYMBOLS'
    limit = '1000'
    fetch_params = {'apikey': apikey, 'path': path, 'limit': limit, 'filter': mmsid_filter}
    r = requests.get(url_root, params = fetch_params)
    while r.status_code != 200:
        r = requests.get(url_root, params = fetch_params)
    return r


def create_unres_master_report(xml_report):

    root = etree.fromstring(xml_report.content)
    resultset = root.findall("./QueryResult/ResultXml/*/*")
    a = etree.Element('response')
    resultset.pop(0)
    for result in resultset:
        a.append(deepcopy(result))

    records = []
    rows = a.getchildren()
    for row in rows:
            record = {}
            gcs = row.getchildren()
            for column in gcs:
                record[column.tag] = column.text
            records.append(record)

    report_df = pd.DataFrame.from_dict(records, dtype=str)
    report_df = report_df.rename(columns={'{urn:schemas-microsoft-com:xml-analysis:rowset}Column0': 'Column0', 
        '{urn:schemas-microsoft-com:xml-analysis:rowset}Column1': '909 Cataloging Status Field', 
        '{urn:schemas-microsoft-com:xml-analysis:rowset}Column2': 'MMS ID',
        '{urn:schemas-microsoft-com:xml-analysis:rowset}Column3': 'Title', 
        '{urn:schemas-microsoft-com:xml-analysis:rowset}Column4': 'Library Code', 
        '{urn:schemas-microsoft-com:xml-analysis:rowset}Column5': 'Location Code', 
        '{urn:schemas-microsoft-com:xml-analysis:rowset}Column6': 'OCLC Number in Alma'})
    report_df = report_df.drop('Column0', 1)
    report_df = report_df[['MMS ID', 'OCLC Number in Alma', 'Title', '909 Cataloging Status Field', 'Library Code', 'Location Code']]

    unresxref_df = pd.read_csv('unresxref.csv')
    unresxref_df = unresxref_df.astype('str')
    unres_master_df = pd.merge(report_df, unresxref_df, how='left', on='MMS ID')
    return unres_master_df 


def create_symbol_unres_reports(unres_master_df):

    unres_mnd = unres_master_df.loc[unres_master_df['Library Code'].str.contains('DUMD') & unres_master_df['909 Cataloging Status Field'].str.contains('MND')]
    unres_mll = unres_master_df.loc[unres_master_df['Library Code'].str.contains('TLAW') & unres_master_df['909 Cataloging Status Field'].str.contains('MLL')]
    unres_mcr = unres_master_df.loc[unres_master_df['Library Code'].str.contains('CUMC') & unres_master_df['909 Cataloging Status Field'].str.contains('MCR')]
    unres_mnx = unres_master_df.loc[unres_master_df['Library Code'].str.contains('MBRIG') & unres_master_df['909 Cataloging Status Field'].str.contains('MNX')]
    unres_mnu = unres_master_df.loc[unres_master_df['Library Code'].str.contains('T') & unres_master_df['909 Cataloging Status Field'].str.contains('MNU')]

    all_report_frames = {'mnd': unres_mnd, 'mll': unres_mll, 'mcr': unres_mcr, 'mnx': unres_mnx, 'mnu': unres_mnu}

    for symbol, frame in all_report_frames.items():

        if not frame.empty:
            today = str(date.today())
            outfile = symbol + '_datasync_unresolved_' + today + '.xlsx'
            frame = frame[['MMS ID', 'OCLC Number in Alma', 'Title', '909 Cataloging Status Field', 'Library Code', 'Location Code', 'Staging OCN']]
            wb = openpyxl.Workbook()
            ws = wb.active
            for row in dataframe_to_rows(frame, index=False, header=True):
                ws.append(row)
            wb.save(outfile)


def main():

    oclc_report_files = [f for f in os.listdir() if re.match('.*unresxrefrpt.*', f)]
    if len(oclc_report_files) != 1:
    	unresfile = input('unresxrefrpt file not found. Please supply filename: ')
    else:
    	unresfile = str(oclc_report_files[0])
    print('Parsing unresxrefrpt file...')
    unresrept_parse(unresfile)
    print('Building report filter...')
    mmsid_filter = build_report_filter()
    apikey = get_apikey()
    print('Fetching Alma Analytics report...')
    xml_report = get_analytics_report(mmsid_filter, apikey)
    print('Creating master report...')
    unres_master_df = create_unres_master_report(xml_report)
    print('Building reports for each OCLC symbol...')
    create_symbol_unres_reports(unres_master_df)
    print('Done')

if __name__=='__main__':
    main()