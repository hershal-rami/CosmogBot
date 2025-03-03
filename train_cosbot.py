import json
import random
import os

#horizontal direction same indecies as horizontal
WEAKNESS = {
    "Normal" :   [1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1],
    "Fire" :     [1,1,2,1,1,1,1,1,2,1,1,1,2,1,1,1,1,1],
    "Water" :    [1,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1],
    "Electric" : [1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1],
    "Grass" :    [1,2,1,1,1,2,1,2,1,2,1,2,1,1,1,1,1,1],
    "Ice" :      [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,1,2,1],
    "Fighting" : [1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,2],
    "Poison" :   [1,1,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1],
    "Ground" :   [1,1,2,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1],
    "Flying" :   [1,1,1,2,1,2,1,1,1,1,1,1,2,1,1,1,1,1],
    "Psychic" :  [1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2],
    "Bug" :      [1,2,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1],
    "Rock" :     [1,1,2,1,2,1,2,1,2,1,1,1,1,1,1,1,2,1],
    "Ghost" :    [1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1],
    "Dragon" :   [1,1,1,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2],
    "Dark" :     [1,1,1,1,1,1,2,1,1,1,1,2,1,1,1,1,1,2],
    "Steel" :    [1,2,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1],
    "Fairy" :    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,2,1],
}

RESISTANCE = {
    "Normal" :   [1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1],
    "Fire" :     [1,0.5,1,1,0.5,0.5,1,1,1,1,1,0.5,1,1,1,1,0.5,0.5],
    "Water" :    [1,0.5,0.5,1,1,0.5,1,1,1,1,1,1,1,1,1,1,0.5,1],
    "Electric" : [1,1,1,0.5,1,1,1,1,1,0.5,1,1,1,1,1,1,0.5,1],
    "Grass" :    [1,1,0.5,0.5,0.5,1,1,1,0.5,1,1,1,1,1,1,1,1,1],
    "Ice" :      [1,1,1,1,1,1,0.5,1,1,1,1,1,1,1,1,1,1,1],
    "Fighting" : [1,1,1,1,1,1,1,1,1,1,1,0.5,0.5,1,1,0.5,1,1],
    "Poison" :   [1,1,1,1,0.5,1,0.5,0.5,1,1,1,0.5,1,1,1,1,1,0.5],
    "Ground" :   [1,1,1,0,1,1,1,0.5,1,1,1,1,0.5,1,1,1,1,1],
    "Flying" :   [1,1,1,1,0.5,1,0.5,1,0,1,1,0.5,1,1,1,1,1,1],
    "Psychic" :  [1,1,1,1,1,1,0.5,1,1,1,0.5,1,1,1,1,1,1,1],
    "Bug" :      [1,1,1,1,0.5,1,0.5,1,0.5,1,1,1,1,1,1,1,1,1],
    "Rock" :     [0.5,0.5,1,1,1,1,1,0.5,1,0.5,1,1,1,1,1,1,1,1],
    "Ghost" :    [0,1,1,1,1,1,0,0.5,1,1,1,0.5,1,1,1,1,1,1],
    "Dragon" :   [1,0.5,0.5,0.5,0.5,1,1,1,1,1,1,1,1,1,1,1,1,1],
    "Dark" :     [1,1,1,1,1,1,1,1,1,1,0,1,1,0.5,1,0.5,1,1],
    "Steel" :    [0.5,1,1,1,0.5,0.5,1,0,1,0.5,0.5,0.5,0.5,1,0.5,1,0.5,0.5],
    "Fairy" :    [1,1,1,1,1,1,0.5,1,1,1,1,0.5,1,1,0,0.5,1,1],
}

utility_moves = ["Stealth Rock", "Defog", "Rapid Spin", "Spikes", "Toxic Spikes", "Sticky Webs", "Wish", "Haze", "Clear Smog", "Will-o-Wisp", "Tailwind", "Reflect", "Light Screen"]

pkmn = {}
with open("./data/Pokemon_Feature_Data.json", "r") as file:
    pkmn = json.load(file)

pkmn_names = []
for p in pkmn:
    pkmn_names.append(p)

train_data = {}
if os.path.exists("./data/Training_data.json"):
    with open("./data/Training_data.json", "r") as file:
        train_data = json.load(file)
else:
    with open("./data/Training_data.json", "w") as file:
        json.dump(train_data,file)
curr_index = 0
if train_data:
    curr_index = int(max(list(map(int, train_data.keys()))))

user_input = ""

while user_input != "done":

    num_on_team = random.choice([2,3,4,5])

    starting_team = []
    for i in range(num_on_team):
        
        choice = random.choice(pkmn_names)

        while choice in starting_team or sum(pkmn[choice]["STATS"]) < 440:
            choice = random.choice(pkmn_names)
        starting_team.append(choice)

    choice = random.choice(pkmn_names)
    while choice in starting_team or sum(pkmn[choice]["STATS"]) < 440:
        choice = random.choice(pkmn_names)
    
    new_mon = choice

    print("\n\n\n\n\n\n")
    print("**********************")
    print("     CURRENT TEAM     ")
    print("**********************")

    print("-------------------------------------------------------------------------------------")
    print("| Name  ".ljust(19) + "  | HP  | ATK | DEF | SPA | SPD | SPE |" + " TYPE1".ljust(12) + "| TYPE2".ljust(12) + "|".rjust(3))

    atk = []
    defen = []
    spatk = []
    spdef = []
    spe = []
    weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    num_weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    res =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    types = {}
    utility = []
    for mon in starting_team:
        print("-------------------------------------------------------------------------------------")
        print("| " + mon[:19].ljust(19) + "| " + str(pkmn[mon]["STATS"][0]).ljust(4) + "| " + str(pkmn[mon]["STATS"][1]).ljust(4) + "| " + str(pkmn[mon]["STATS"][2]).ljust(4) \
            + "| " + str(pkmn[mon]["STATS"][3]).ljust(4) + "| " + str(pkmn[mon]["STATS"][4]).ljust(4) + "| " + str(pkmn[mon]["STATS"][5]).ljust(4)  \
            + "| " + pkmn[mon]["TYPE"][0].ljust(11) + "| " + str(pkmn[mon]["TYPE"][1]).ljust(12) + "|")
        
        atk.append(pkmn[mon]["STATS"][1])
        defen.append(pkmn[mon]["STATS"][2])
        spatk.append(pkmn[mon]["STATS"][3])
        spdef.append(pkmn[mon]["STATS"][4])
        spe.append(pkmn[mon]["STATS"][5])

        for w in range(len(pkmn[mon]["TYPE_EFFECTIVE"])):
            if pkmn[mon]["TYPE_EFFECTIVE"][w] > 1:
                weak[w] += pkmn[mon]["TYPE_EFFECTIVE"][w]
                num_weak[w] += 1
        
        for r in range(len(pkmn[mon]["TYPE_EFFECTIVE"])):
            if pkmn[mon]["TYPE_EFFECTIVE"][r] < 1:
                res[r] += 1
        for t in range(len(pkmn[mon]["TYPE"])):
            if types.get(pkmn[mon]["TYPE"][t]):
                types[pkmn[mon]["TYPE"][t]] += 1
            else:
                types[pkmn[mon]["TYPE"][t]] = 1

        for move in pkmn[mon]["UTILITY"]:
            if move not in utility:
                utility.append(move)

    total_weak = 0
    for i in range(len(weak)):
        temp = weak[i] - 2 * res[i]

        if temp <= 0:
            temp = 0
        total_weak += temp

    total_unres = 0
    for i in range(len(weak)):
        temp = num_weak[i] - res[i]

        if temp <= 1:
            temp = 0
        total_unres += temp

    total_repeat = 0
    for i in types:
        if types[i] >= 3 and i != None and i != "None":
            total_repeat += types[i] - 2
        
    total_res = 0
    for i in range(len(weak)):

        if res[i] < 2:
            total_res += 1

    print("-------------------------------------------------------------------------------------")
    print()
    
    print("=====================================================================================")
    print("FEATURES".rjust(46))
    print("=====================================================================================")
    print("Difference between average ATK and SPATK:", str(abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))))
    print("Difference between average DEF and SPDEF:", str(abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))))
    print("Average Speed Stat:", str((sum(spe) /len(spe))))
    print("Severity of weaknesses:", total_weak)
    print("Number of Types you don't have at least 2 resistances for:", total_res)
    print("Number of Types you have at least 2 unresisted weaknesses for:", total_unres)
    print("Number of repeated types (over 2):", total_repeat)
    print("Utility moves:", utility)


    print("\n")
    print("*********************")
    print("     NEW POKEMON     ")
    print("*********************")
    print("-------------------------------------------------------------------------------------")
    print("| Name  ".ljust(19) + "  | HP  | ATK | DEF | SPA | SPD | SPE |" + " TYPE1".ljust(12) + "| TYPE2".ljust(12) + "|".rjust(3))
    print("-------------------------------------------------------------------------------------")
    print("| " + "Pokemon 0".ljust(19) + "| " + str(pkmn[new_mon]["STATS"][0]).ljust(4) + "| " + str(pkmn[new_mon]["STATS"][1]).ljust(4) + "| " + str(pkmn[new_mon]["STATS"][2]).ljust(4) \
            + "| " + str(pkmn[new_mon]["STATS"][3]).ljust(4) + "| " + str(pkmn[new_mon]["STATS"][4]).ljust(4) + "| " + str(pkmn[new_mon]["STATS"][5]).ljust(4)  \
            + "| " + pkmn[new_mon]["TYPE"][0].ljust(11) + "| " + str(pkmn[new_mon]["TYPE"][1]).ljust(12) + "|")
    print("-------------------------------------------------------------------------------------")



    new_mon_2 = new_mon

    stats2 = list(pkmn[new_mon]["STATS"])

    stat_change = random.choice([0, 20, 20, 30, 30, 30, 30, 40, 40, 50])

    stat_to_change = random.choice([1,1,2,2,3,3,4,4,5])
    stat_to_change_2 = stat_to_change
    while stat_to_change_2 == stat_to_change:
        stat_to_change_2 = random.choice([1,1,2,2,3,3,4,4,5])

    stats2[stat_to_change] += stat_change
    stats2[stat_to_change_2] -= stat_change

    type_list = list(WEAKNESS.keys())
    type2 = list(pkmn[new_mon]["TYPE"])

    if random.random() < 0.5:
        if type2[1] != None:
            type_list.remove(type2[1])
            type2[0] = random.choice(type_list)
        else:
            type2[0] = random.choice(type_list)
    elif random.random() < 0.5:
        type_list.remove(type2[0])
        type_list.append(None)
        type2[1] = random.choice(type_list)

    
    type_effective2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    if type2[1] == None:
        for i in range(len(WEAKNESS[type2[0]])):
            type_effective2[i] = WEAKNESS[type2[0]][i] * RESISTANCE[type2[0]][i]
    else:
        for i in range(len(WEAKNESS[type2[0]])):
            type_effective2[i] = WEAKNESS[type2[0]][i] * RESISTANCE[type2[0]][i] * WEAKNESS[type2[1]][i] * RESISTANCE[type2[1]][i]

    utility2 = []
    new_utility = []
    for move in pkmn[new_mon]["UTILITY"]:
        if move not in utility:
            new_utility.append(move)

    for move in new_utility:
        if random.random() < 0.5:
            utility2.append(move)

    for move in utility_moves:
        if random.random() < 1/len(utility_moves) and move not in utility2:
            utility2.append(move)

    
    print("-------------------------------------------------------------------------------------")
    print("| " + "Pokemon 1".ljust(19) + "| " + str(stats2[0]).ljust(4) + "| " + str(stats2[1]).ljust(4) + "| " + str(stats2[2]).ljust(4) \
            + "| " + str(stats2[3]).ljust(4) + "| " + str(stats2[4]).ljust(4) + "| " + str(stats2[5]).ljust(4)  \
            + "| " + type2[0].ljust(11) + "| " + str(type2[1]).ljust(12) + "|")
    print("-------------------------------------------------------------------------------------")


    atk.append(pkmn[new_mon]["STATS"][1])
    defen.append(pkmn[new_mon]["STATS"][2])
    spatk.append(pkmn[new_mon]["STATS"][3])
    spdef.append(pkmn[new_mon]["STATS"][4])
    spe.append(pkmn[new_mon]["STATS"][5])

    for w in range(len(pkmn[new_mon]["TYPE_EFFECTIVE"])):
        if pkmn[new_mon]["TYPE_EFFECTIVE"][w] > 1:
            weak[w] += pkmn[new_mon]["TYPE_EFFECTIVE"][w]

    for t in range(len(pkmn[new_mon]["TYPE"])):
            if types.get(pkmn[new_mon]["TYPE"][t]):
                types[pkmn[new_mon]["TYPE"][t]] += 1
            else:
                types[pkmn[new_mon]["TYPE"][t]] = 1

    for r in range(len(pkmn[new_mon]["TYPE_EFFECTIVE"])):
        if pkmn[new_mon]["TYPE_EFFECTIVE"][r] < 1:
            res[r] += 1

    new_utility = []
    for move in pkmn[new_mon]["UTILITY"]:
        if move not in utility:
            new_utility.append(move)

    total_weak = 0
    for i in range(len(weak)):
        temp = weak[i] - 2 * res[i]

        if temp <= 0:
            temp = 0
        total_weak += temp

    total_unres = 0
    for i in range(len(weak)):
        temp = num_weak[i] - res[i]

        if temp <= 1:
            temp = 0
        total_unres += temp

    total_repeat = 0
    for i in types:
        if types[i] >= 3 and i != None and i != "None":
            total_repeat += types[i] - 2
        
    total_res = 0
    for i in range(len(weak)):

        if res[i] < 2:
            total_res += 1

    print("-------------------------------------------------------------------------------------")
    print()
    
    print("=====================================================================================")
    print("FEATURES WITH ADDING POKEMON 0".rjust(46))
    print("=====================================================================================")
    print("Difference between average ATK and SPATK:", str(abs(sum(atk) /len(atk) - sum(spatk) / len(spatk)) ))
    print("Difference between average DEF and SPDEF:", str(abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))))
    print("Average Speed Stat:", str((sum(spe) /len(spe))))
    print("Severity of weaknesses:", total_weak)
    print("Number of Types you don't have at least 2 resistances for:", total_res)
    print("Number of Types you have at least 2 unresisted weaknesses for:", total_unres)
    print("Number of repeated types (over 2):", total_repeat)
    print("Utility moves:", new_utility)

    atk.remove(pkmn[new_mon]["STATS"][1])
    defen.remove(pkmn[new_mon]["STATS"][2])
    spatk.remove(pkmn[new_mon]["STATS"][3])
    spdef.remove(pkmn[new_mon]["STATS"][4])
    spe.remove(pkmn[new_mon]["STATS"][5])

    for w in range(len(pkmn[new_mon]["TYPE_EFFECTIVE"])):
        if pkmn[new_mon]["TYPE_EFFECTIVE"][w] > 1:
            weak[w] -= pkmn[new_mon]["TYPE_EFFECTIVE"][w]
            num_weak[w] -= 1

    for t in range(len(pkmn[new_mon]["TYPE"])):
            if types.get(pkmn[new_mon]["TYPE"][t]):
                types[pkmn[new_mon]["TYPE"][t]] -= 1
    
    for r in range(len(pkmn[new_mon]["TYPE_EFFECTIVE"])):
        if pkmn[new_mon]["TYPE_EFFECTIVE"][r] < 1:
            res[r] -= 1


    atk.append(stats2[1])
    defen.append(stats2[2])
    spatk.append(stats2[3])
    spdef.append(stats2[4])
    spe.append(stats2[5])

    for w in range(len(type_effective2)):
        if type_effective2[w] > 1:
            weak[w] += type_effective2[w]

    for t in type2:
        if types.get(t):
            types[t] += 1
        else:
            types[t] = 1
    
    for r in range(len(type_effective2)):
        if type_effective2[r] < 1:
            res[r] += 1

    new_utility = []
    for move in utility2:
        if move not in utility:
            new_utility.append(move)

    total_weak = 0
    for i in range(len(weak)):
        temp = weak[i] - 2 * res[i]

        if temp <= 0:
            temp = 0
        total_weak += temp

    total_unres = 0
    for i in range(len(weak)):
        temp = num_weak[i] - res[i]

        if temp <= 1:
            temp = 0
        total_unres += temp

    total_repeat = 0
    for i in types:
        if types[i] >= 3 and i != None and i != "None":
            total_repeat += types[i] - 2
        
    total_res = 0
    for i in range(len(weak)):

        if res[i] < 2:
            total_res += 1

    print("-------------------------------------------------------------------------------------")
    print()
    
    print("=====================================================================================")
    print("FEATURES WITH ADDING POKEMON 1".rjust(46))
    print("=====================================================================================")
    print("Difference between average ATK and SPATK:", str(abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))))
    print("Difference between average DEF and SPDEF:", str(abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))))
    print("Average Speed Stat:", str((sum(spe) /len(spe))))
    print("Severity of weaknesses:", total_weak)
    print("Number of Types you don't have at least 2 resistances for:", total_res)
    print("Number of Types you have at least 2 unresisted weaknesses for:", total_unres)
    print("Number of repeated types (over 2):", total_repeat)
    print("Utility moves:", new_utility)

    print("\n")
    better = input("Which Pokemon is better to add to this team? (enter 0 or 1 or 2 for no real difference / nonsensical Pokemon) ")
    while better != "1" and better != "0" and better != "2":
        better = input("Wrong input enter again")

    if(better != 2):
        curr_index += 1
        train_data[curr_index] = {"STARTING_TEAM": starting_team, "POKEMON_0": new_mon, "POKEMON_1": {"STATS": stats2, "TYPE": type2, "UTILITY": utility2, "TYPE_EFFECTIVENESS": type_effective2}}
        with open("./data/Training_data.json", "w") as wfile:
            json.dump(train_data, wfile,indent=4)

    print("\n")
    user_input = input("Press enter to continue or type done and then enter to stop: ")

