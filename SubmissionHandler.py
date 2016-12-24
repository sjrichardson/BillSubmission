
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import smtplib
import json
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
credential_file = 'credentials.json'
bills = []
"""populate json_data with data from the credentials file"""
json_data = []
with open(credential_file, 'r') as reader:
    json_data = json.load(reader)
print(json_data)
"""Google sheet access code taken from Google quick start drive"""
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = json_data['google']['client_secret']
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    #starting row is the current_row as labeled in credentials.json
    spreadsheetId = json_data['google']['spreadsheet_id']
    rangeName = 'A%d:N' % json_data['google']['current_row']
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            #creates new bill with all of the provided information from each column
            bill = Bill_info(row[0],row[1],row[2],row[3],row[4],row[5],row[6],
            row[7],row[8],row[9],row[10],row[11],row[12],row[13])
        update_current_row(len(values))

def format_file(bill):
    pass

def send_mail():
    pass
"""Updates current_row in the json file"""
def update_current_row(current_row):
    with open(credential_file,"w") as f:
        #update json_data with current_row
        json_data['google']['current_row'] = current_row
        #formatting_json
        json_string = str(json_data)
        json_string = json_string.replace("u","")
        json_string = json_string.replace("\'", "\"")
        #overwrite json file with json_string
        f.write(json_string)
class Bill_info(object):
    """docstring for ."""
    def __init__(self, timestamp, bill_title, total_cost, committee, num_participants, can_participate,
    date, time, location, materials, description, author, author_email, floor):
        self.timestamp = timestamp
        self.bill_title = bill_title
        self.total_cost = total_cost
        self.committee = committee
        self.num_participants = num_participants
        self.can_participate = can_participate
        self.date = date
        self.time = time
        self.location = location
        self.materials = materials
        self.description = description
        self.author = author
        self.author_email = author_email
        self.floor = floor

if __name__ == '__main__':
    main()
