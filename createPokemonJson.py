import json
import gspread
from bot import DOCS

pokeDict = {}

with open("data/pokeStats.json", "r") as file:
    pokeDict = json.load(file)

for i in range(len(DOCS) - 1):
    doc = DOCS[i]
    sa = gspread.service_account("data/credentialsfile.json")
    sheet = sa.open(doc)
    boardSheet = sheet.worksheet("Draft Board")
    rawData = boardSheet.get_all_values()

    for col in rawData[2:]:
        for pokemon in col:
            if pokemon != "":
                print(pokemon)
                if pokeDict.get(pokemon,True):
                    pokeDict[pokemon.strip()] = {"Kills":0, "Deaths":0, "Matches Played":0, "Matches Eligible":0}

with open("data/pokeStats.json", "w") as file:
    json.dump(pokeDict,file, indent = 4)