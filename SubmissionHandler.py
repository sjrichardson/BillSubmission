
from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import smtplib
import json
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
credential_file = "credentials.json"
bills = []
"""populate json_data with data from the credentials file"""
json_data = []
with open(credential_file, 'r') as reader:
    json_data = json.load(reader)
#current fields needed for each bill
bill_fields = ["Title of bill:", "Total Estimated Cost:", "Committee:",
"Number of Participants:", "Who can participate:", "Date And Time of Activity:",
"Location:","Materials Needed:", "Description of Bill:", "Proposed by:", "Floor:"]

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
            format_file(bill)
        update_current_row(len(values))

def format_file(bill):
    c = canvas.Canvas("bill.pdf")
    init_x = 740
    init_y = 30
    x_spacing = 40
    bill_pos = 0
    c.save()

def send_mail():
    pass
"""Updates current_row in the json file"""
def update_current_row(difference):
    with open(credential_file,"w") as f:
        #update json_data with current_row
        json_data['google']['current_row'] += difference
        #formatting_json
        json_string = json.dumps(json_data, ensure_ascii=False)
        #overwrite json file with json_string
        f.write(json_string)
class Bill_info(object):
    """docstring for ."""
    def __init__(self, timestamp, bill_title, total_cost, committee, num_participants, can_participate,
    date, time, location, materials, description, author, author_email, floor):
        self.bill_values = [timestamp, bill_title, total_cost, committee,
        num_participants, can_participate, "%s %s" % (date, time), location,
        materials, description, author, author_email,floor]

if __name__ == '__main__':
    main()
