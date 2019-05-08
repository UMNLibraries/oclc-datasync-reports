'''This script fetches predefined deleted holdings reports from Alma Analytics
for each OCLC symbol managed under UMMBL (MNU, MND, MCR, MNX, MLL), parses the reports, 
and outputs a CSV file for the OCLC Datasync process.'''

import csv
import requests
import pandas as pd
from datetime import date
from lxml import etree
from copy import deepcopy
from datasync_unres_analytics import get_apikey

def get_delete_reports(paths):
    url_root = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    apikey = get_apikey()
    limit = '1000'

    raw_reports = []
    for path in paths:
        print('Fetching ' + path)
        fetch_params = {'apikey': apikey, 'path': path, 'limit': limit}
        r = requests.get(url_root, params = fetch_params)

        while r.status_code != 200:
            r = requests.get(url_root, params = fetch_params)
            print(r.status_code)
            print(r.text)
            print("Trying again...")
    
        raw_reports.append(r.content)
        
    return raw_reports

def parse_delete_reports(raw_reports):
    records = []
    for report in raw_reports:
        root = etree.fromstring(report)
        resultset = root.findall("./QueryResult/ResultXml/*/*")
        resultset.pop(0)
        a = etree.Element('response')
        for result in resultset:
            a.append(deepcopy(result))
        rows = a.getchildren()
        for row in rows:
            record = {}
            kids = row.getchildren()
            for column in kids:
                record[column.tag] = column.text
            records.append(record)
    return records


def process_delete_report(parsed_report):
    data = pd.DataFrame.from_dict(parsed_report, dtype=str)
    data = data.rename(columns={'{urn:schemas-microsoft-com:xml-analysis:rowset}Column0': 'Column0', 
                            '{urn:schemas-microsoft-com:xml-analysis:rowset}Column1': 'Library Code',
                            '{urn:schemas-microsoft-com:xml-analysis:rowset}Column2': 'OCN',
                            '{urn:schemas-microsoft-com:xml-analysis:rowset}Column3': 'Column3'})
    data = data.drop('Column0', 1)
    data = data.drop('Column3', 1)
    data = data[['OCN', 'Library Code']]
    return data


def main():
    path_mnd = '/shared/University of Minnesota/Reports/OCLC withdrawal project/Operational/MND Last Copy Withdrawn Feed for Script'
    path_mnu = '/shared/University of Minnesota/Reports/OCLC withdrawal project/Operational/MNU Last Copy Withdrawn Feed for Script'
    path_mnx = '/shared/University of Minnesota/Reports/OCLC withdrawal project/Operational/MNX Last Copy Withdrawn Feed for Script'
    path_mll = '/shared/University of Minnesota/Reports/OCLC withdrawal project/Operational/MLL Last Copy Withdrawn Feed for Script'
    path_mcr = '/shared/University of Minnesota/Reports/OCLC withdrawal project/Operational/MCR Last Copy Withdrawn Feed for Script'
    paths = [path_mcr, path_mll, path_mnd, path_mnx, path_mnu]

    raw_reports = get_delete_reports(paths)
    print('Parsing reports...')
    parsed_report = parse_delete_reports(raw_reports)
    print('Finishing up...')
    processed_report = process_delete_report(parsed_report)

    today = str(date.today()).replace('-', '')

    outfile = '1031465.UMMBL.deletes.' + today + '.csv'
    header = ['OCN', 'Library Code']
    processed_report.to_csv(outfile, columns = header, index = False)
    print('Done!')

if __name__ == "__main__":
    main()