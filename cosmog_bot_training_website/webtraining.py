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
    "Ice" :      [1,1,1,1,1,0.5,1,1,1,1,1,1,1,1,1,1,1,1],
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

utility_moves = ["Stealth Rock", "Defog", "Rapid Spin", "Spikes", "Toxic Spikes", "Sticky Webs", "Wish", "Haze", "Clear Smog", "Will-o-Wisp", "Tailwind", "Reflect", "Light Screen", "U-Turn"]


type_names = ["Normal","Fire","Water","Electric","Grass","Ice","Fighting","Poison","Ground","Flying","Psychic","Bug","Rock","Ghost","Dragon","Dark", "Steel","Fairy"]
pkmn = {}
with open("./data/Pokemon_Feature_Data.json", "r") as file:
    pkmn = json.load(file)

pkmn_names = []
for p in pkmn:
    pkmn_names.append(p)

"""
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
"""

def get_training_example():

    current_team_stats = ""
    new_stats_0 = ""
    new_stats_1 = ""
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

    current_team_stats+=("\n\n\n\n\n\n")
    current_team_stats+=("**********************")
    current_team_stats+="\n"
    current_team_stats+=("     CURRENT TEAM     ")
    current_team_stats+="\n"
    current_team_stats+=("**********************")
    current_team_stats+="\n"

    current_team_stats+=("-------------------------------------------------------------------------------------")
    current_team_stats+="\n"
    current_team_stats+=("| Name  ".ljust(19) + "  | HP  | ATK | DEF | SPA | SPD | SPE |" + " TYPE1".ljust(12) + "| TYPE2".ljust(12) + "|".rjust(3))
    current_team_stats+="\n"

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
        current_team_stats+=("-------------------------------------------------------------------------------------")
        current_team_stats+="\n"
        current_team_stats+=("| " + mon[:19].ljust(19) + "| " + str(pkmn[mon]["STATS"][0]).ljust(4) + "| " + str(pkmn[mon]["STATS"][1]).ljust(4) + "| " + str(pkmn[mon]["STATS"][2]).ljust(4) \
            + "| " + str(pkmn[mon]["STATS"][3]).ljust(4) + "| " + str(pkmn[mon]["STATS"][4]).ljust(4) + "| " + str(pkmn[mon]["STATS"][5]).ljust(4)  \
            + "| " + pkmn[mon]["TYPE"][0].ljust(11) + "| " + str(pkmn[mon]["TYPE"][1]).ljust(12) + "|")
        current_team_stats+="\n"
        
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

    current_team_stats+=("-------------------------------------------------------------------------------------")
    current_team_stats+="\n"
    
    current_team_stats+=("=====================================================================================")
    current_team_stats+="\n"
    current_team_stats+=("FEATURES".rjust(46))
    current_team_stats+="\n"
    current_team_stats+=("=====================================================================================")
    current_team_stats+="\n"
    current_team_stats+=("Difference between average ATK and SPATK: " + str(abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))))
    current_team_stats+="\n"
    current_team_stats+=("Difference between average DEF and SPDEF: " + str(abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))))
    current_team_stats+="\n"
    current_team_stats+=("Average Speed Stat: " + str((sum(spe) /len(spe))))
    current_team_stats+="\n"
    current_team_stats+=("Severity of weaknesses: " + str(total_weak))
    current_team_stats+="\n"
    current_team_stats+=("Number of Types you don't have at least 2 resistances for: " + str(total_res))
    current_team_stats+="\n"
    current_team_stats+=("Number of Types you have at least 2 unresisted weaknesses for: "+ str(total_unres))
    current_team_stats+="\n"
    current_team_stats+=("Number of repeated types (over 2): "+ str(total_repeat))
    current_team_stats+="\n"
    current_team_stats+=("Utility moves: "+ str(utility))
    current_team_stats+="\n"
    current_team_stats+=str(" ".ljust(9) + "|Norm" + "|Fire" + "|Wate" + "|Elec" + "|Gras" + "|Ice " + \
                            "|Figh" + "|Pois" + "|Grou" + "|Flyi" + "|Psyc" + "|Bug " + "|Rock" + "|Ghos" + \
                                "|Drag" + "|Dark" + "|Stee" + "|Fair|\n")
    current_team_stats += "Num Weak".ljust(9) + "|"

    for w in num_weak:
        current_team_stats+=str(w).ljust(4) + "|"
    current_team_stats+="\n"
    
    current_team_stats += "Num Res".ljust(9) + "|"

    for r in res:
        current_team_stats+=str(r).ljust(4) + "|"
    current_team_stats+="\n"
    current_team_stats+="Speed Tiers|0-30  |30-60 |60-90 |90-120|120+  |\n"
    spe_tiers = {"<30":0, "<60":0,"<90":0,"<120":0,"120+":0}
    for spe_stat in spe:

        if spe_stat < 30:
            spe_tiers["<30"] += 1
        elif spe_stat < 60:
            spe_tiers["<60"] += 1
        elif spe_stat < 90:
            spe_tiers["<90"] += 1
        elif spe_stat < 120:
            spe_tiers["<120"] += 1
        else:
            spe_tiers["120+"] += 1
    current_team_stats += "           |"
    for spe_stat in spe_tiers:
        current_team_stats += str(spe_tiers[spe_stat]).ljust(6) + "|"
    current_team_stats += "\n"



    

    new_stats_0+=("---------------")
    new_stats_0+=("\n")
    new_stats_0+=("| " + "Pokemon 0".ljust(12) + "|\n")
    new_stats_0+=("---------------")
    new_stats_0+="\n| " + "HP".ljust(6) + "| " + str(pkmn[new_mon]["STATS"][0]).ljust(4)+ "| " + "\n| " + "ATK".ljust(6) \
            + "| " + str(pkmn[new_mon]["STATS"][1]).ljust(4)+ "| " + "\n| " + "DEF".ljust(6) + "| " + str(pkmn[new_mon]["STATS"][2]).ljust(4)+ "| "  \
            + "\n| " + "SPATK".ljust(6) + "| " + str(pkmn[new_mon]["STATS"][3]).ljust(4)+ "| "  \
            + "\n| " + "SPDEF".ljust(6) + "| " + str(pkmn[new_mon]["STATS"][4]).ljust(4) + "| " \
            + "\n| " + "SPE".ljust(6) + "| " + str(pkmn[new_mon]["STATS"][5]).ljust(4)+ "| \n"  
    new_stats_0+=("---------------")
    new_stats_0+="\n| " + pkmn[new_mon]["TYPE"][0].ljust(12) + "|\n| " + str(pkmn[new_mon]["TYPE"][1]).ljust(12) + "|"
    new_stats_0+=("\n")
    new_stats_0+=("---------------")
    new_stats_0+=("\n")



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


    new_stats_1+=("---------------")
    new_stats_1+=("\n")
    new_stats_1+=("| " + "Pokemon 1".ljust(12) + "|\n")
    new_stats_1+=("---------------")
    new_stats_1+="\n| " + "HP".ljust(6) + "| " + str(stats2[0]).ljust(4)+ "| " + "\n| " + "ATK".ljust(6) \
            + "| " + str(stats2[1]).ljust(4)+ "| " + "\n| " + "DEF".ljust(6) + "| " + str(stats2[2]).ljust(4)+ "| "  \
            + "\n| " + "SPATK".ljust(6) + "| " + str(stats2[3]).ljust(4)+ "| "  \
            + "\n| " + "SPDEF".ljust(6) + "| " + str(stats2[4]).ljust(4) + "| " \
            + "\n| " + "SPE".ljust(6) + "| " + str(stats2[5]).ljust(4)+ "| \n"  
    new_stats_1+=("---------------")
    new_stats_1+="\n| " + type2[0].ljust(12) + "|\n| " + str(type2[1]).ljust(12) + "|"
    new_stats_1+=("\n")
    new_stats_1+=("---------------")
    new_stats_1+=("\n")


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

    

    new_stats_0+=("===================================================")
    new_stats_0+=("\n")
    new_stats_0+=("FEATURES AFTER ADDING POKEMON 0")
    new_stats_0+=("\n")
    new_stats_0+=("===================================================")
    new_stats_0+=("\n")
    new_stats_0+=("Difference between ATK and SPATK: "+ str(int(abs(sum(atk) /len(atk) - sum(spatk) / len(spatk)) )))
    new_stats_0+=("\n")
    new_stats_0+=("Difference between DEF and SPDEF: "+ str(int(abs(sum(defen) /len(defen) - sum(spdef) / len(spdef)))))
    new_stats_0+=("\n")
    new_stats_0+=("Average Speed Stat: "+ str((sum(spe) /len(spe))))
    new_stats_0+=("\n")
    new_stats_0+=("Severity of weaknesses: "+ str(total_weak))
    new_stats_0+=("\n")
    new_stats_0+=("Types you don't have at least 2 resistances for: "+ str(total_res))
    new_stats_0+=("\n")
    new_stats_0+=("Number of unresisted weaknesses (over 2): "+ str(total_unres))
    new_stats_0+=("\n")
    new_stats_0+=("Number of repeated types (over 2): "+ str(total_repeat))
    new_stats_0+=("\n")
    new_stats_0+=("Utility moves: "+ str(new_utility))
    new_stats_0+=("\n")
    new_stats_0+= "Weak to: "

    print(type_list)
    
    for w in range(len(pkmn[new_mon]["TYPE_EFFECTIVE"])):
        if pkmn[new_mon]["TYPE_EFFECTIVE"][w] > 1:
            print(w)
            new_stats_0 += type_names[w][0:4]
            new_stats_0 += ", "
    new_stats_0 += "\n"
    new_stats_0+= "Resists: "

    for r in range(len(pkmn[new_mon]["TYPE_EFFECTIVE"])):
        if pkmn[new_mon]["TYPE_EFFECTIVE"][r] < 1:
            new_stats_0 += type_names[r][0:4]
            new_stats_0 += ", "
    new_stats_0 += "\n"

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
            num_weak[w] += 1

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

    
    new_stats_1+=("===================================================")
    new_stats_1+=("\n")
    new_stats_1+=("FEATURES AFTER ADDING POKEMON 1")
    new_stats_1+=("\n")
    new_stats_1+=("===================================================")
    new_stats_1+=("\n")
    new_stats_1+=("Difference between ATK and SPATK: "+ str(int(abs(sum(atk) /len(atk) - sum(spatk) / len(spatk)))))
    new_stats_1+=("\n")
    new_stats_1+=("Difference between DEF and SPDEF: "+ str(int(abs(sum(defen) /len(defen) - sum(spdef) / len(spdef)))))
    new_stats_1+=("\n")
    new_stats_1+=("Average Speed Stat: "+ str((sum(spe) /len(spe))))
    new_stats_1+=("\n")
    new_stats_1+=("Severity of weaknesses: "+ str(total_weak))
    new_stats_1+=("\n")
    new_stats_1+=("Types you don't have at least 2 resistances for: "+ str(total_res))
    new_stats_1+=("\n")
    new_stats_1+=("Number of unresisted weaknesses (over 2): "+ str(total_unres))
    new_stats_1+=("\n")
    new_stats_1+=("Number of repeated types (over 2): "+ str(total_repeat))
    new_stats_1+=("\n")
    new_stats_1+=("Utility moves: "+ str(new_utility))

    new_stats_1+=("\n")
    new_stats_1+= "Weak to: "
    
    for w in range(len(type_effective2)):
        if type_effective2[w] > 1:
            new_stats_1 += type_names[w][0:4]
            new_stats_1 += ", "
    new_stats_1 += "\n"
    new_stats_1+= "Resists: "

    for r in range(len(type_effective2)):
        if type_effective2[r] < 1:
            new_stats_1 += type_names[r][0:4]
            new_stats_1 += ", "
    new_stats_1 += "\n"

    train_example = {"STARTING_TEAM": starting_team, "POKEMON_0": new_mon, "POKEMON_1": {"STATS": stats2, "TYPE": type2, "UTILITY": utility2, "TYPE_EFFECTIVENESS": type_effective2}}

    return current_team_stats ,new_stats_0, new_stats_1, train_example


