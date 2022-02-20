import json
import gspread

pokeDict = {}
DOCS = ["MBTL LC Doc TEST VER", "Copy of MBTL VGC Doc - Solgaleo"]

with open("pokeStats.json", "r") as file:
    pokeDict = json.load(file)

for doc in DOCS:
    sa = gspread.service_account("credentialsfile.json")
    sheet = sa.open(doc)
    boardSheet = sheet.worksheet("Draft Board")
    rawData = boardSheet.get_all_values()

    for col in rawData[2:]:
        for pokemon in col:
            if pokemon != "":
                print(pokemon)
                if pokeDict.get(pokemon,True):
                    pokeDict[pokemon.strip()] = {"Kills":0, "Deaths":0, "Matches Played":0, "Matches Eligible":0}

with open("pokeStats.json", "w") as file:
    json.dump(pokeDict,file, indent = 4)