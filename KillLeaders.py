import json
from os import kill

import gspread
import pandas as pd

# Setup - Doc name and relevant ranges
DOCS = ["MBTL LC Doc TEST VER","MBTL Monotype Draft TEST VER", "MBTL Kill Counter"]
LUN = 0
SOL = 1

DATA_RANGE = 'A3:E158'
LEADERS_RANGE = 'I40:L59'
COACH_RANGE = 'I61:J72'


# Pull rosters from spreadsheet and create JSON with empty statistics
def convert_to_json(doc_num):
    # Connect to spreadsheet
    sa = gspread.service_account("credentialsfile.json")
    sheet = sa.open(DOCS[doc_num])
    sheet_instance = sheet.worksheet("Rosters")

    # Remove outside empty cells and swap Roster columns into rows
    raw_data = sheet_instance.get_all_values()[1:]
    values = list(zip(*raw_data))[1:-1]
    
    # Compile dictionary from the raw data
    all_teams = {}
    for row in values:
        # Skip non-roster rows
        if row[0] == 'Cost':
            continue

        # more than one team in each row
        i = 0
        while i < len(row) - 1:
            coach = row[i]
            team_info = [{"Team": row[i+1]}]
            i += 2
            
            # rosters are separated by an empty cell
            while i < len(row) - 1 and row[i] != '':
                # skip point cost rows
                if row[i].isnumeric():
                    i += 1
                    continue

                pokemon = row[i]
                team_info.append({pokemon:{"Kills":0, "Deaths":0, "K/D":0}})
                i = i + 1
            
            all_teams[coach] = team_info
            i += 1

    # Print dictionary to JSON file
    filename = 'kill_leaders_' + str(doc_num) + '.json'
    with open(filename, 'w+') as fp:
        json.dump(all_teams, fp, indent=4)

"-Whenever a match is completed, automatically open the correct JSON and update the kill statistics"
# Open the corresponding JSON file and update based on differentials from the completed match
def update_json(doc_num, differentials):
    filename = 'kill_leaders_' + str(doc_num) + '.json'
    with open(filename, 'w') as fp:
        data = json.load(fp)
    # TODO finish    
    return


"-Whenever the calculate kill leaders command is called, open the correct JSON, convert to arrays, and use existing pandas code"
# Open the correct JSON and return kill leaders data
def calculate_kill_leaders(doc_num):
    filename = 'kill_leaders_' + str(doc_num) + '.json'
    with open(filename, 'w') as fp:
        data = json.load(fp)
    
    # for coach in data:
    # TODO complete
    return

# Code for update of kill leaders spreadsheet
def update_spreadsheet(doc_num):
    # Connect to spreadsheet doc
    sa = gspread.service_account("credentialsfile.json")
    sheet = sa.open(DOCS[doc_num])
    sheet_instance = sheet.worksheet("LC")
    raw_data = sheet_instance.get_all_values()

    # Get relevant trainer data
    values = [x for x in sheet_instance.get(DATA_RANGE) if x != []] # accounting for the blank lines between coaches

    # Properly assign coach names to each pokemon
    for i in range(len(values)):
        if values[i][0] != '':
            curr_coach = values[i][0]
        else:
            values[i][0] = curr_coach

    # Sort based on overall kills, then K/D, then alphabetical order
    df = pd.DataFrame(values, columns=["Coach", "Pokemon", "Kills", "Deaths", "K/D"])
    df = df.astype({"Kills": int, "Deaths": int, "K/D": int})
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
        output = [row[1], int(row[2]), int(row[3]), row[0]]
        values.append(output)

    sheet_instance.update(LEADERS_RANGE, values)

    # Sort coach stats and print to Google Sheet
    coach_stats = sorted(coach_stats.items(), key=lambda x:x[1], reverse=True)
    values = []
    for i in range(len(coach_stats)):
        coach, num = coach_stats[i]
        values.append([coach, num])
    sheet_instance.update(COACH_RANGE, values)

    print("Processing complete. Please check the Google Sheet for accuracy.")