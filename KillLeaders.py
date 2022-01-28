from os import kill
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

# IDs of the MBTL Kill Leaders spreadsheet
SPREADSHEET_ID = '1UgqTBDZwNv8-ZSzCfeKXsPkFvCacMP2K9YP9agEIiBg'
SHEET_ID = '656636448'

# Provide scope for IAM account
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# Add credentials to the account from local key
#creds = ServiceAccountCredentials.from_json_keyfile_name('mbtl-kill-leaders-d3a7d99f9e5c.json', scope)
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret_606396420727-i5pigfj11fopip9lt3imrp5e4k1f7t2o.apps.googleusercontent.com.json', scope)

# Pull sheet instance
service = build('sheets', 'v4', credentials=creds)
sheet_instance = service.spreadsheets()

# Get relevant trainer data
result = sheet_instance.values().get(spreadsheetId=SPREADSHEET_ID, range='A3:E145').execute()
values = result.get('values', [])
values = [x for x in values if x != []] # accounting for the blank lines between coaches

# Properly assign coach names to each pokemon
for i in range(len(values)):
    if values[i][0] != '':
        curr_coach = values[i][0]
    else:
        values[i][0] = curr_coach

# Sort based on overall kills, then K/D, then alphabetical order
df = pd.DataFrame(values, columns=["Coach", "Pokemon", "Kills", "Deaths", "K/D"])
df = df.sort_values(["Kills", "K/D", "Pokemon"], ascending=(False, False, True))
kill_leaders = df.head(20)

# Organize data and print to the Google Sheet
values = []
coach_stats = {}
for i in range(20):
    # Get raw row data from dataframe
    row = kill_leaders.iloc[i].values.tolist()

    # Keep track of how many kill leaders each coach has
    if row[0] in coach_stats:
        coach_stats[row[0]] += 1
    else:
        coach_stats[row[0]] = 1
    
    # Reorder as Pokemon, Kills, Deaths, Coach
    output = [row[1], row[2], row[3], row[0]]
    values.append(output)
body = {'values' : values}
result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range='I38:L57',
    valueInputOption='USER_ENTERED', body=body).execute()

# Sort coach stats and print to Google Sheet
coach_stats = sorted(coach_stats.items(), key=lambda x:x[1], reverse=True)
values = []
for i in range(len(coach_stats)):
    coach, num = coach_stats[i]
    values.append([coach, num])
body = {'values' : values}
result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range='I61:J72',
    valueInputOption='USER_ENTERED', body=body).execute()

print("Processing complete. Please check the Google Sheet for accuracy.")