from re import L
from webbrowser import get
import pandas as pd

import gspread
from gspread_formatting import *

DOC = "MBTL LC Doc TEST VER"

def getTeamColors():
    """
    This function gets formatting objects for each team.
    :RETURN: a dictionary where the keys are each team name and the values
            are a formatting object for that team
    """

    #open the sheet
    sa = gspread.service_account("credentialsfile.json")
    sheet = sa.open(DOC)
    standingsSheet = sheet.worksheet("Standings")

    #see how many teams there are
    rows = standingsSheet.row_count

    start = "C3"
    end = "C" + str(rows - 1)
    cellRange = start + ":" + end

    #get a list of all the names
    teamNames = standingsSheet.get(cellRange)
    teamColors = {}

    #get the sheet formatting objects for each team
    for i in range(3, rows):
        teamColors[teamNames[i - 3][0]] = get_user_entered_format(standingsSheet, "C"+str(i))

    return teamColors


def getStandings():
    """
    This function gets the current standings of the league.
    :RETURN: a list that is just the excel sheet.
            A 2d grid with each cell of the sheet in it
    """

    #open the sheet and get the data from the stadnings 
    sa = gspread.service_account("credentialsfile.json")
    sheet = sa.open(DOC)
    standingsSheet = sheet.worksheet("Standings")
    rawData = standingsSheet.get_all_values()

    return rawData


def getFormattedStandings():
    """
    Takes current standings of the league and reformats them into a single
    string that can be displayed to the user by the bot upon request
    """
    # remove additional row and col on the top and left side
    raw_data = getStandings()[1::]
    for i, row in enumerate(raw_data):
        raw_data[i] = row[1::]

    # store column names separately
    columns = raw_data[0]
    raw_data = raw_data[1::]

    # create pandas df and use to restructure output
    df = pd.DataFrame(raw_data, columns=columns)
    return df.to_string(index=False)


def updateStandings(team1, team2):
    """
    This function changes the standings on the sheet.

    :TEAM1: a dictionary formmated like
            {pokemon: (killNum, DeathNum), pokemon2: (killNum, DeathNum)..., 
            TeamName:"something", Coach:"someone", "Winner": bool, 
            DiffChange:integer change in differential}
    
    :TEAM2: same as team1

    :RETURN: None
    """

    RANK = 1
    TEAMNAME = 2
    WINS = 3
    LOSSES = 4
    DIFF = 5

    teamColors = getTeamColors()
    current = getStandings()

    name1 = team1["TeamName"]
    name2 = team2["TeamName"]

    for team in current:
        
        #cheack if each team is team1 then update wins. losses and differential
        if(team[TEAMNAME] == name1):

            if(team1["Winner"]):
                team[WINS] = str(int(team[WINS]) + 1)
            else:
                team[LOSSES] = str(int(team[LOSSES]) + 1)

            team[DIFF] = str(int(team[DIFF]) + team1["DiffChange"])

        #same as team1
        if(team[TEAMNAME] == name2):

            if(team2["Winner"]):
                team[WINS] = str(int(team[WINS]) + 1)
            else:
                team[LOSSES] = str(int(team[LOSSES]) + 1)

            team[DIFF] = str(int(team[DIFF]) + team2["DiffChange"])

    
    #re-sort the rankings
    for i in range(2, len(current) - 1):

        #if less wins, swap down
        if(int(current[i][WINS]) < int(current[i + 1][WINS])):

            #swap the position of the two teams
            tempTeam = current[i]
            current[i] = current[i+1]
            current[i+1] = tempTeam

            #also swap their respective ranks
            tempRank = current[i+1][RANK]
            current[i + 1][RANK] = current[i][RANK]
            current[i][RANK] = tempRank

        #if there's an equal number of wins, go by differential
        if(int(current[i][WINS]) == int(current[i + 1][WINS])):

            if(int(current[i][DIFF]) < int(current[i + 1][DIFF])):

                #swap the position of the two teams
                tempTeam = current[i]
                current[i] = current[i+1]
                current[i+1] = tempTeam

                #also swap their respective ranks
                tempRank = current[i+1][RANK]
                current[i + 1][RANK] = current[i][RANK]
                current[i][RANK] = tempRank

            #if diff is even, just don't swap, we have no way to know the tiebreaker here
    
    sa = gspread.service_account("credentialsfile.json")
    sheet = sa.open(DOC)
    standingsSheet = sheet.worksheet("Standings")

    #throw in the new results
    standingsSheet.update(current)

    #reformat and color the cells
    for i in range(3, len(current) - 1):

        teamName = standingsSheet.acell("C" + str(i)).value

        #for some reason if the text was black it wasn't stored so I have to do that manually
        if(teamColors[teamName].textFormat.foregroundColor == None):
            teamColors[teamName].textFormat.foregroundColor = Color(0,0,0)
   
        format_cell_range(standingsSheet, "C" + str(i), teamColors[teamName])
        format_cell_range(standingsSheet, "G" + str(i), teamColors[teamName])


def getRosters():
    """
    This function gets all of the pokemon drafted by each team.
    :RETURN: a list of dictionaries, where each dictionary is a team,
            in the format of {"Pokemon": ["Chimchar", "Snivy", ...], "TeamName": "Cool Guys", "Coach": "Me"}
    """

    #open the sheet and get the data from the rosters tab 
    sa = gspread.service_account("credentialsfile.json")
    sheet = sa.open(DOC)
    rosterSheet = sheet.worksheet("Rosters")
    rawData = rosterSheet.get_all_values()

    #because of how it works i have to split the list in half to access all the teams
    row1 = rawData[1 : len(rawData) // 2 - 1]
    row2 = rawData[len(rawData) // 2 + 1:-1]

    #create a list that will be the reutrn value
    team_list = []

    #loop through the data and group together the rosters in the form
    #{"Pokemon": ["Chimchar", "Snivy", ...], "TeamName": "Cool Guys", "Coach": "Me"}
    for i in range(1, len(row1[0]) - 1):

        team = {}
        team["Pokemon"] = []

        for j in range(0, len(row1)):
            
            if(j == 0):
                team["Coach"] = row1[j][i]
            elif(j == 1):
                team["TeamName"] = row1[j][i]
            else:
                team["Pokemon"].append(row1[j][i])
        
        team_list.append(team)


    #same thing but for the other half of the teams
    for i in range(1, len(row2[0]) - 1):

        team = {}
        team["Pokemon"] = []

        for j in range(0, len(row1)):
            if(j == 0):
                team["Coach"] = row2[j][i]
            elif(j == 1):
                team["TeamName"] = row2[j][i]
            else:
                team["Pokemon"].append(row2[j][i])
        
        team_list.append(team)

    #return the list of all the teams
    return team_list


def updateMatchResults(result):
    #get rid of all the stuff before the kill info and break it up by line
    print(result)
    result = result.split("\n")[3:]
    print(result)

    #store all kill info in 2 dictionaires
    #Team1 and Team2
    #where team 1 is of the format {pokemon: (killNum, DeathNum), pokemon2: (killNum, DeathNum) ...}
    team1 = {}
    for i in range(6):
        pokeStat = result[i].split(" ")

        #retrieve stats from message
        pokemon = pokeStat[0]
        killNum = pokeStat[2]
        deathNum = pokeStat[-3]

        team1[pokemon] = (killNum, deathNum)

    team2 = {}
    for i in range(8,14):
        pokeStat = result[i].split(" ")

        #retrieve stats from message
        pokemon = pokeStat[0]
        killNum = pokeStat[2]
        deathNum = pokeStat[-3]

        team2[pokemon] = (killNum, deathNum)

    print(team1)
    print(team2)

    #tally up the deaths
    deaths1 = 0
    for mon in team1:
        
        #if that mon died
        if team1[mon][1] == "1":
            deaths1 += 1

    deaths2 = 0
    for mon in team2:
        
        #if that mon died
        if team2[mon][1] == "1":
            deaths2 += 1

    #calculate the winner
    #Seems redundant at first but I think we have to do this
    #because some showdown names are inconsistant with team or coach names
    #so instead of dealing with that it's easier to recalculate
    if(deaths1 >= 6):
        team1["Winner"] = False
        team2["Winner"] = True

    elif(deaths2 >= 6):
        team1["Winner"] = True
        team2["Winner"] = False

    else:
        team1["Winner"] = False
        team2["Winner"] = False

    #calculate change in differential
    team1["DiffChange"] = deaths2 - deaths1
    team2["DiffChange"] = deaths1 - deaths2


    #get the rosters to determine which teams battled
    rosters = getRosters()

    #look for a roster that has the pokemon in it, that's the team that battled
    team1Mon = list(team1.keys())[0]
    team2Mon = list(team2.keys())[0]

    for team in rosters:

        if team1Mon in team["Pokemon"]:
            team1["TeamName"] = team["TeamName"]
            team1["Coach"] = team["Coach"]
        
        elif team2Mon in team["Pokemon"]:
            team2["TeamName"] = team["TeamName"]
            team2["Coach"] = team["Coach"]

    updateStandings(team1, team2)
    
    print("Standings have been updated!!")
