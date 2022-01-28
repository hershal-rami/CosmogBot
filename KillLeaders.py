from os import kill
import pandas as pd

import gspread

# Connect to spreadsheet doc
LC_DOC = "MBTL LC Doc TEST VER"
KILL_DOC = "MBTL Kill Counter"

sa = gspread.service_account("credentialsfile.json")
sheet = sa.open(KILL_DOC)
sheet_instance = sheet.worksheet("LC")
raw_data = sheet_instance.get_all_values()

# Get relevant trainer data
cell_range = 'A3:E158'
values = [x for x in sheet_instance.get(cell_range) if x != []] # accounting for the blank lines between coaches

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

sheet_instance.update('I40:L59', values)

# Sort coach stats and print to Google Sheet
coach_stats = sorted(coach_stats.items(), key=lambda x:x[1], reverse=True)
values = []
for i in range(len(coach_stats)):
    coach, num = coach_stats[i]
    values.append([coach, num])
sheet_instance.update('I61:J72', values)

print("Processing complete. Please check the Google Sheet for accuracy.")