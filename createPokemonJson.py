import json

pokeDict = {}

with open("pokemon.txt", "r") as file:

    for line in file:
        pokeDict[line.strip()] = {"Kills":0, "Deaths":0, "Games Played":0, "Games Eligible":0}

with open("pokeStats.json", "w") as file:
    json.dump(pokeDict,file, indent = 4)