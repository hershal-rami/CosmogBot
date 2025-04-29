import json
from os import listdir
from os.path import isfile, join
import numpy as np
import random
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
import pandas as pd
from imblearn.under_sampling import EditedNearestNeighbours
from sklearn.model_selection import KFold
import os
import torch
import torch.nn as nn


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
    "Psychic" :  [1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,1],
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

BANNED = ["Pokestar Black Belt", "Pokestar White Door", "Pokestar Black Door", "Pokestar Spirit", "Pokestar F-002", "Pokestar F-00", "Pokestar Monster", "Pokestar Giant",
          "Pokestar Transport", "Pokestar MT2", "Pokestar MT", "Pokestar Brycen-Man", "Pokestar UFO", "Pokestar Smeargle", "Cresceidon", "Hemogoblin", "Scattervein", 
          "Ababo", "Saharaja", "Saharascal", "Venomicon", "Protowatt", "Dorsoil", "Duohm", "Monohm", "Nohface", "Chromera", "Miasmaw", "Miasmite", "Astrolotl", "Solotl",
          "Equilibra", "Justyke", "Snaelstrom", "Coribalis", "Swirlpool", "Smokomodo", "Smoguana", "Smogecko", "Caribolt", "Electrelk", "Fawnifer", "Jumbao", "Mumbao",
          "Pajantom", "Kerfluffle", "Pluffle", "Crucibelle", "Naviathan", "Caimanoe", "Floatoy", "Plasmanta", "Snugglow", "Volkraken", "Volkritter", "Cawmodore", "Cawdet",
          "Malaconda", "Brattler", "Aurumoth", "Argalis", "Cupra", "Mollux", "Necturna", "Necturine", "Tomohawk", "Scratchet", "Voodoom", "Voodoll", "Krilowatt", "Colossoil",
          "Cyclohm", "Kitsunoh", "Arghonaut", "Privatyke", "Stratagem", "Tactite", "Rebble", "Fidgit", "Breezil", "Pyroak", "Flarelm", "Embirch", "Revenankh", "Syclant", "Syclar",
          "MissingNo.", "Mewtwo", "Lugia", "Ho-Oh","Kyogre", "Groudon", "Rayquaza", "Deoxys","Dialga", "Palkia", "Giratina", "Arceus", "Reshiram", "Zekrom","Genesect", "Xerneas",
          "Yveltal", "Solgaleo", "Lunala", "Pheramosa", "Magearna","Marshadow","Naganadel", "Zacian", "Zamazenta", "Eternatus", "Flutter Mane", "Koraidon", "Miraidon",
          "Pokestar UFO-2", "Venomicon-Epilogue", "Crucibelle-Mega", "Butterfree-Gmax", "Alakazam-Mega", "Machamp-Gmax", "Gengar-Mega", "Kingler-Gmax", "Lapras-Gmax", "Eevee-Starter",
          "Snorlax-Gmax", "Mewtwo-Mega-X", "Blaziken-Mega", "Salamence-Mega", "Metagross-Mega", "Latias-Mega", "Latios-Mega", "Kyogre-Primal", "Groudon-Primal", "Rayquaza-Mega",
          "Deoxys-Attack", "Lucario-Mega", "Dialga-Origin", "Palkia-Origin", "Giratina-Origin", "Shaymin-Sky", "Arceus-Bug", "Garbodor-Gmax", "Kyurem-Black", "Genesect-Douse",
          "Greninja-Bond", "Xerneas-Neutral", "Gumshoos-Totem", "Vikavolt-Totem", "Ribombee-Totem", "Araquanid-Totem", "Lurantis-Totem", "Salazzle-Totem", "Togedemaru-Totem",
          "Kommo-o-Totem", "Necrozma-Dusk-Mane", "Magearna-Original", "Melmetal-Gmax", "Rillaboom-Gmax", "Cinderace-Gmax","Inteleon-Gmax", "Corviknight-Gmax", "Orbeetle-Gmax",
          "Drednaw-Gmax", "Coalossal-Gmax", "Flapple-Gmax", "Appletun-Gmax", "Sandaconda-Gmax", "Centiskorch-Gmax","Hatterene-Gmax", "Grimmsnarl-Gmax", "Alcremie-Gmax", "Copperajah-Gmax",
          "Duraludon-Gmax", "Zacian-Crowned", "Zamazenta-Crowned", "Eternatus-Eternamax", "Zarude-Dada", "Calyrex-Ice", "Venusaur-Gmax", "Blastoise-Gmax", "Raticate-Alola-Totem",
          "Gengar-Gmax", "Marowak-Alola-Totem", "Eevee-Gmax", "Mewtwo-Mega-Y", "Arceus-Dark", "Kyurem-White","Genesect-Shock", "Genesect-Ash", "Zygarde-Complete", "Mimikyu-Totem",
          "Necrozma-Dawn-Wings","Toxtricity-Gmax","Urshifu-Gmax","Calyrex-Shadow", "Terapagos-Stellar","Charizard-Gmax","Meowth-Gmax","Arceus-Dragon","Genesect-Burn","Mimikyu-Busted-Totem",
          "Necrozma-Ultra","Toxtricity-Low-Key-Gmax","Urshifu-Rapid-Strike-Gmax","Arceus-Electric","Genesect-Chill","Ogerpon-Teal-Tera","Arceus-Fairy","Ogerpon-Wellspring-Tera",
          "Arceus-Fighting","Ogerpon-Hearthflame-Tera","Arceus-Fire", "Ogerpon-Cornerstone-Tera","Arceus-Flying","Arceus-Ghost","Arceus-Grass","Arceus-Ground", "Arceus-Ice", 
          "Arceus-Poison", "Arceus-Psychic","Pikachu-Gmax","Arceus-Rock", "Arceus-Steel", "Arceus-Water", "Pokestar Humanoid", "Breezi"]

utility_moves = ["Stealth Rock", "Defog", "Rapid Spin", "Spikes", "Toxic Spikes", "Sticky Webs", "Wish", "Haze", "Clear Smog", "Will-o-Wisp", "Tailwind", "Reflect", "Light Screen", "U-turn", "Baton Pass"]
doubles_utility = ["Follow Me", "Rage Powder", "Helping Hand"]

type_names = ["Normal","Fire","Water","Electric","Grass","Ice","Fighting","Poison","Ground","Flying","Psychic","Bug","Rock","Ghost","Dragon","Dark", "Steel","Fairy"]


def count_examples():
    onlyfiles = [join("./data/cosmog_training_data/", f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f))]

    num_people = 0 
    num_examples = 0

    for file in onlyfiles:
        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)

            num_people += 1

            for k in json_f:
                num_examples += 1

    print("Unique Annotators", num_people)
    print("Num Examples", num_examples)

def training_plot():
    onlyfiles = [join("./data/cosmog_training_data/", f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f))]

    

    ex = []
    name = []

    for file in onlyfiles:
        num_examples = 0
        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)

            for k in json_f:
                num_examples += 1
            
            ex.append(num_examples)
            name.append(file.split("/")[-1].split("_training")[0])

    plt.figure(figsize=(12, 8))
    sort_i = np.argsort(np.array(ex))
    print(np.array(name)[sort_i])
    print(np.array(ex)[sort_i])
    plt.barh(np.array(name)[sort_i], np.array(ex)[sort_i])
    plt.title("Number of Training Examples Generated by User")
    plt.ylabel("User")
    plt.xlabel("Number of Training Examples")
    plt.yticks(np.array(name)[sort_i],np.array(name)[sort_i],rotation=0, fontsize="7")
    plt.savefig("./data/annotation_plot")
    



def from_json_to_numpy_A(data_folder = "./data/no_outlier_training_data/"):

    """
    Features Included
    difference between atk and spatk
    difference between def and spdef
    average speed
    rocks
    removal
    other utility moves
    weakness score
    resistaqnce score
    unresisted score
    repeated types
    """

    featureset_name = "A"

    pkmn = {}

    data_0 = []
    data_1 = []
    labels = []
    combined = []
    with_anno_label = []

    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)

    onlyfiles = [join(data_folder, f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    anno_i = 0
    for file in onlyfiles:

        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)
            print(file)


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

            for ex in json_f:

                for mon in json_f[ex]["STARTING_TEAM"]:

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
                        if move not in utility and move in utility_moves:
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

                new_utility = []

                new_mon = json_f[ex]["POKEMON_0"]

                for move in pkmn[new_mon]["UTILITY"]:
                    if move not in utility and move in utility_moves:
                        new_utility.append(move)

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

                
                atk_sp_diff = abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))
                def_sp_diff = abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))
                avg_speed = (sum(spe) /len(spe))

                rocks = 0
                removal = 0
                everything_else = 0
                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1
                
                for move in new_utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1

                stats_0 = [atk_sp_diff, def_sp_diff, avg_speed, rocks, removal, everything_else, total_weak, total_res, total_unres, total_repeat]

                stats_1 = []


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

                stats2 = json_f[ex]["POKEMON_1"]["STATS"]
                type_effective2 = json_f[ex]["POKEMON_1"]["TYPE_EFFECTIVENESS"]
                type2 = json_f[ex]["POKEMON_1"]["TYPE"]
                utility2 = json_f[ex]["POKEMON_1"]["UTILITY"]

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

                rocks = 0
                removal = 0
                everything_else = 0

                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1
                
                for move in utility2:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1

                atk_sp_diff = abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))
                def_sp_diff = abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))
                avg_speed = (sum(spe) /len(spe))

                stats_1 = [atk_sp_diff, def_sp_diff, avg_speed, rocks, removal, everything_else, total_weak, total_res, total_unres, total_repeat]
                #print(stats_0)
                #print(stats_1)
                #print(json_f[ex]["Better"])
                #print("------------------------------------------------------------------------")
                
                if json_f[ex]["Better"] == 0:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(0)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(1)
                else:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(1)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(0)

                anno_i += 1

    np.save("./data/training_processed/" + featureset_name + "_pkmn0_data.npy",np.array(data_0))
    np.save("./data/training_processed/" + featureset_name + "_pkmn1_data.npy",np.array(data_1))
    np.save("./data/training_processed/" + featureset_name + "_combined_data.npy",np.array(combined))
    np.save("./data/training_processed/" + featureset_name + "_combined_annotator_data.npy",np.array(with_anno_label))
    np.save("./data/training_processed/" + featureset_name + "_labels_data.npy",np.array(labels))



def from_json_to_numpy_B(data_folder = "./data/no_outlier_training_data/"):

    """
    Features Included
    difference between num phys attackers and spatkers
    difference between num phys defenders and spdefenders
    speed tiers
    rocks
    removal
    pivot
    other utility moves
    weakness score
    resistaqnce score
    unresisted score
    repeated types
    """

    featureset_name = "B"

    pkmn = {}

    data_0 = []
    data_1 = []
    labels = []
    combined = []
    with_anno_label = []

    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)

    onlyfiles = [join(data_folder, f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    anno_i = 0
    for file in onlyfiles:

        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)
            print(file)


            atk = 0
            defen = 0
            spatk = 0
            spdef = 0
            spe = []
            weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            num_weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            res =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            types = {}
            utility = []

            for ex in json_f:

                for mon in json_f[ex]["STARTING_TEAM"]:

                    if pkmn[mon]["STATS"][1] > pkmn[mon]["STATS"][3] *1.3:
                        atk += 1
                    elif pkmn[mon]["STATS"][1] * 1.3 < pkmn[mon]["STATS"][3]:
                        spatk += 1
                    else:
                        if pkmn[mon]["STATS"][1] > 100:
                            atk += 1
                        if pkmn[mon]["STATS"][3] > 100:
                            spatk += 1

                    if pkmn[mon]["STATS"][2] > pkmn[mon]["STATS"][4] *1.3:
                        defen += 1
                    elif pkmn[mon]["STATS"][2] * 1.3 < pkmn[mon]["STATS"][4]:
                        spdef += 1
                    else:
                        if pkmn[mon]["STATS"][2] > 100:
                            defen += 1
                        if pkmn[mon]["STATS"][4] > 100:
                            spdef += 1

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
                        if move not in utility and move in utility_moves:
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

                new_utility = []

                new_mon = json_f[ex]["POKEMON_0"]

                for move in pkmn[new_mon]["UTILITY"]:
                    if move not in utility and move in utility_moves:
                        new_utility.append(move)

                if pkmn[new_mon]["STATS"][1] > pkmn[new_mon]["STATS"][3] *1.3:
                    atk += 1
                elif pkmn[new_mon]["STATS"][1] * 1.3 < pkmn[new_mon]["STATS"][3]:
                    spatk += 1
                else:
                    if pkmn[new_mon]["STATS"][1] > 100:
                        atk += 1
                    if pkmn[new_mon]["STATS"][3] > 100:
                        spatk += 1

                if pkmn[new_mon]["STATS"][2] > pkmn[new_mon]["STATS"][4] *1.3:
                    defen += 1
                elif pkmn[new_mon]["STATS"][2] * 1.3 < pkmn[new_mon]["STATS"][4]:
                    spdef += 1
                else:
                    if pkmn[new_mon]["STATS"][2] > 100:
                        defen += 1
                    if pkmn[new_mon]["STATS"][4] > 100:
                        spdef += 1

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

                
                atk_sp_diff = abs(atk - spatk)
                def_sp_diff = abs(defen - spdef)
                less_30 = 0
                less_60 = 0
                less_90 = 0
                less_120 = 0
                plus_120 = 0

                for spe_stat in spe:

                    if spe_stat < 30:
                        less_30 += 1
                    elif spe_stat < 60:
                        less_60 += 1
                    elif spe_stat < 90:
                        less_90 += 1
                    elif spe_stat < 120:
                        less_120 += 1
                    else:
                        plus_120 += 1


                rocks = 0
                removal = 0
                pivot = 0
                everything_else = 0
                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1
                
                for move in new_utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1

                stats_0 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, rocks, removal, pivot, everything_else, total_weak, total_res, total_unres, total_repeat]

                stats_1 = []


                if pkmn[new_mon]["STATS"][1] > pkmn[new_mon]["STATS"][3] *1.3:
                    atk -= 1
                elif pkmn[new_mon]["STATS"][1] * 1.3 < pkmn[new_mon]["STATS"][3]:
                    spatk -= 1
                else:
                    if pkmn[new_mon]["STATS"][1] > 100:
                        atk -= 1
                    if pkmn[new_mon]["STATS"][3] > 100:
                        spatk -= 1

                if pkmn[new_mon]["STATS"][2] > pkmn[new_mon]["STATS"][4] *1.3:
                    defen -= 1
                elif pkmn[new_mon]["STATS"][2] * 1.3 < pkmn[new_mon]["STATS"][4]:
                    spdef -= 1
                else:
                    if pkmn[new_mon]["STATS"][2] > 100:
                        defen -= 1
                    if pkmn[new_mon]["STATS"][4] > 100:
                        spdef -= 1

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

                stats2 = json_f[ex]["POKEMON_1"]["STATS"]
                type_effective2 = json_f[ex]["POKEMON_1"]["TYPE_EFFECTIVENESS"]
                type2 = json_f[ex]["POKEMON_1"]["TYPE"]
                utility2 = json_f[ex]["POKEMON_1"]["UTILITY"]

                if stats2[1] > stats2[3] *1.3:
                    atk += 1
                elif stats2[1] * 1.3 < stats2[3]:
                    spatk += 1
                else:
                    if stats2[1] > 100:
                        atk += 1
                    if stats2[3] > 100:
                        spatk += 1

                if stats2[2] > stats2[4] *1.3:
                    defen += 1
                elif stats2[2] * 1.3 < stats2[4]:
                    spdef += 1
                else:
                    if stats2[2] > 100:
                        defen += 1
                    if stats2[4] > 100:
                        spdef += 1
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

                rocks = 0
                removal = 0
                everything_else = 0
                pivot = 0

                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1
                
                for move in utility2:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1

                atk_sp_diff = abs(atk - spatk)
                def_sp_diff = abs(defen - spdef)
                less_30 = 0
                less_60 = 0
                less_90 = 0
                less_120 = 0
                plus_120 = 0

                for spe_stat in spe:

                    if spe_stat < 30:
                        less_30 += 1
                    elif spe_stat < 60:
                        less_60 += 1
                    elif spe_stat < 90:
                        less_90 += 1
                    elif spe_stat < 120:
                        less_120 += 1
                    else:
                        plus_120 += 1

                stats_1 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, rocks, removal, pivot, everything_else, total_weak, total_res, total_unres, total_repeat]
                #print(stats_0)
                #print(stats_1)
                #print(json_f[ex]["Better"])
                #print("------------------------------------------------------------------------")
                
                if json_f[ex]["Better"] == 0:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(0)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(1)
                else:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(1)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(0)

                anno_i += 1

    np.save("./data/training_processed/" + featureset_name + "_pkmn0_data.npy",np.array(data_0))
    np.save("./data/training_processed/" + featureset_name + "_pkmn1_data.npy",np.array(data_1))
    np.save("./data/training_processed/" + featureset_name + "_combined_data.npy",np.array(combined))
    np.save("./data/training_processed/" + featureset_name + "_combined_annotator_data.npy",np.array(with_anno_label))
    np.save("./data/training_processed/" + featureset_name + "_labels_data.npy",np.array(labels))



def from_json_to_numpy_C(data_folder = "./data/no_outlier_training_data/"):

    """
    Features Included
    difference between num phys attackers and spatkers
    difference between num phys defenders and spdefenders
    speed tiers
    rocks
    removal
    pivot
    other utility moves
    weakness score
    resistaqnce score
    unresisted score
    repeated types
    weakness to every type
    resistance to every type
    """

    featureset_name = "C"

    pkmn = {}

    data_0 = []
    data_1 = []
    labels = []
    combined = []
    with_anno_label = []

    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)

    onlyfiles = [join(data_folder, f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    anno_i = 0
    for file in onlyfiles:

        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)
            print(file)


            atk = 0
            defen = 0
            spatk = 0
            spdef = 0
            spe = []
            weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            num_weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            res =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            types = {}
            utility = []

            for ex in json_f:

                for mon in json_f[ex]["STARTING_TEAM"]:

                    if pkmn[mon]["STATS"][1] > pkmn[mon]["STATS"][3] *1.3:
                        atk += 1
                    elif pkmn[mon]["STATS"][1] * 1.3 < pkmn[mon]["STATS"][3]:
                        spatk += 1
                    else:
                        if pkmn[mon]["STATS"][1] > 100:
                            atk += 1
                        if pkmn[mon]["STATS"][3] > 100:
                            spatk += 1

                    if pkmn[mon]["STATS"][2] > pkmn[mon]["STATS"][4] *1.3:
                        defen += 1
                    elif pkmn[mon]["STATS"][2] * 1.3 < pkmn[mon]["STATS"][4]:
                        spdef += 1
                    else:
                        if pkmn[mon]["STATS"][2] > 100:
                            defen += 1
                        if pkmn[mon]["STATS"][4] > 100:
                            spdef += 1

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
                        if move not in utility and move in utility_moves:
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

                new_utility = []

                new_mon = json_f[ex]["POKEMON_0"]

                for move in pkmn[new_mon]["UTILITY"]:
                    if move not in utility and move in utility_moves:
                        new_utility.append(move)

                if pkmn[new_mon]["STATS"][1] > pkmn[new_mon]["STATS"][3] *1.3:
                    atk += 1
                elif pkmn[new_mon]["STATS"][1] * 1.3 < pkmn[new_mon]["STATS"][3]:
                    spatk += 1
                else:
                    if pkmn[new_mon]["STATS"][1] > 100:
                        atk += 1
                    if pkmn[new_mon]["STATS"][3] > 100:
                        spatk += 1

                if pkmn[new_mon]["STATS"][2] > pkmn[new_mon]["STATS"][4] *1.3:
                    defen += 1
                elif pkmn[new_mon]["STATS"][2] * 1.3 < pkmn[new_mon]["STATS"][4]:
                    spdef += 1
                else:
                    if pkmn[new_mon]["STATS"][2] > 100:
                        defen += 1
                    if pkmn[new_mon]["STATS"][4] > 100:
                        spdef += 1

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

                
                atk_sp_diff = abs(atk - spatk)
                def_sp_diff = abs(defen - spdef)
                less_30 = 0
                less_60 = 0
                less_90 = 0
                less_120 = 0
                plus_120 = 0

                for spe_stat in spe:

                    if spe_stat < 30:
                        less_30 += 1
                    elif spe_stat < 60:
                        less_60 += 1
                    elif spe_stat < 90:
                        less_90 += 1
                    elif spe_stat < 120:
                        less_120 += 1
                    else:
                        plus_120 += 1


                rocks = 0
                removal = 0
                pivot = 0
                everything_else = 0
                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1
                
                for move in new_utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1


                stats_0 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, rocks, removal, pivot, everything_else, total_weak, total_res, total_unres, total_repeat]


                for w in num_weak:
                    stats_0.append(w)
                for r in res:
                    stats_0.append(r)
                stats_1 = []


                if pkmn[new_mon]["STATS"][1] > pkmn[new_mon]["STATS"][3] *1.3:
                    atk -= 1
                elif pkmn[new_mon]["STATS"][1] * 1.3 < pkmn[new_mon]["STATS"][3]:
                    spatk -= 1
                else:
                    if pkmn[new_mon]["STATS"][1] > 100:
                        atk -= 1
                    if pkmn[new_mon]["STATS"][3] > 100:
                        spatk -= 1

                if pkmn[new_mon]["STATS"][2] > pkmn[new_mon]["STATS"][4] *1.3:
                    defen -= 1
                elif pkmn[new_mon]["STATS"][2] * 1.3 < pkmn[new_mon]["STATS"][4]:
                    spdef -= 1
                else:
                    if pkmn[new_mon]["STATS"][2] > 100:
                        defen -= 1
                    if pkmn[new_mon]["STATS"][4] > 100:
                        spdef -= 1

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

                stats2 = json_f[ex]["POKEMON_1"]["STATS"]
                type_effective2 = json_f[ex]["POKEMON_1"]["TYPE_EFFECTIVENESS"]
                type2 = json_f[ex]["POKEMON_1"]["TYPE"]
                utility2 = json_f[ex]["POKEMON_1"]["UTILITY"]

                if stats2[1] > stats2[3] *1.3:
                    atk += 1
                elif stats2[1] * 1.3 < stats2[3]:
                    spatk += 1
                else:
                    if stats2[1] > 100:
                        atk += 1
                    if stats2[3] > 100:
                        spatk += 1

                if stats2[2] > stats2[4] *1.3:
                    defen += 1
                elif stats2[2] * 1.3 < stats2[4]:
                    spdef += 1
                else:
                    if stats2[2] > 100:
                        defen += 1
                    if stats2[4] > 100:
                        spdef += 1
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

                rocks = 0
                removal = 0
                everything_else = 0
                pivot = 0

                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1
                
                for move in utility2:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1

                atk_sp_diff = abs(atk - spatk)
                def_sp_diff = abs(defen - spdef)
                less_30 = 0
                less_60 = 0
                less_90 = 0
                less_120 = 0
                plus_120 = 0

                for spe_stat in spe:

                    if spe_stat < 30:
                        less_30 += 1
                    elif spe_stat < 60:
                        less_60 += 1
                    elif spe_stat < 90:
                        less_90 += 1
                    elif spe_stat < 120:
                        less_120 += 1
                    else:
                        plus_120 += 1

                stats_1 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, rocks, removal, pivot, everything_else, total_weak, total_res, total_unres, total_repeat]
                
                for w in num_weak:
                    stats_1.append(w)
                for r in res:
                    stats_1.append(r)
                #print(stats_0)
                #print(stats_1)
                #print(json_f[ex]["Better"])
                #print("------------------------------------------------------------------------")
                
                if json_f[ex]["Better"] == 0:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(0)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(1)
                else:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(1)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(0)

                anno_i += 1

    np.save("./data/training_processed/" + featureset_name + "_pkmn0_data.npy",np.array(data_0))
    np.save("./data/training_processed/" + featureset_name + "_pkmn1_data.npy",np.array(data_1))
    np.save("./data/training_processed/" + featureset_name + "_combined_data.npy",np.array(combined))
    np.save("./data/training_processed/" + featureset_name + "_combined_annotator_data.npy",np.array(with_anno_label))
    np.save("./data/training_processed/" + featureset_name + "_labels_data.npy",np.array(labels))



def from_json_to_numpy_D(data_folder = "./data/no_outlier_training_data/"):

    """
    Features Included
    difference between num phys attackers and spatkers
    difference between num phys defenders and spdefenders
    speed tiers
    weakness score
    repeated types
    """

    featureset_name = "D"

    pkmn = {}

    data_0 = []
    data_1 = []
    labels = []
    combined = []
    with_anno_label = []

    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)

    onlyfiles = [join(data_folder, f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    anno_i = 0
    for file in onlyfiles:

        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)
            print(file)


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

            for ex in json_f:

                for mon in json_f[ex]["STARTING_TEAM"]:

                    atk.append(pkmn[mon]["STATS"][1])
                    defen.append(pkmn[mon]["STATS"][2])
                    spatk.append(pkmn[mon]["STATS"][3])
                    spdef.append(pkmn[mon]["STATS"][4])
                    spe.append(pkmn[mon]["STATS"][5])

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
                        if move not in utility and move in utility_moves:
                            utility.append(move)

                total_weak = 0
                for i in range(len(weak)):
                    temp = weak[i] * (1/(2 * (res[i] + 1/2)))

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

                new_utility = []

                new_mon = json_f[ex]["POKEMON_0"]

                for move in pkmn[new_mon]["UTILITY"]:
                    if move not in utility and move in utility_moves:
                        new_utility.append(move)

                atk.append(pkmn[new_mon]["STATS"][1])
                defen.append(pkmn[new_mon]["STATS"][2])
                spatk.append(pkmn[new_mon]["STATS"][3])
                spdef.append(pkmn[new_mon]["STATS"][4])
                spe.append(pkmn[new_mon]["STATS"][5])

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

                total_weak = 0
                for i in range(len(weak)):
                    temp = weak[i] * (1/(2 * (res[i] + 1/2)))

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
                    if types[i] >= 2 and i != None and i != "None":
                        total_repeat += types[i] - 1
                    
                total_res = 0
                for i in range(len(weak)):

                    if res[i] < 2:
                        total_res += 1

                
                atk_sp_diff = abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))
                def_sp_diff = abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))
                less_30 = 0
                less_60 = 0
                less_90 = 0
                less_120 = 0
                plus_120 = 0

                for spe_stat in spe:

                    if spe_stat < 30:
                        less_30 += 1
                    elif spe_stat < 60:
                        less_60 += 1
                    elif spe_stat < 90:
                        less_90 += 1
                    elif spe_stat < 120:
                        less_120 += 1
                    else:
                        plus_120 += 1


                rocks = 0
                removal = 0
                pivot = 0
                everything_else = 0
                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1
                
                for move in new_utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1

                stats_0 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, rocks, removal, pivot, everything_else, total_weak, total_res, total_unres, total_repeat]
                stats_0 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, total_weak, total_res, total_unres, total_repeat]
                stats_1 = []


                atk.remove(pkmn[new_mon]["STATS"][1])
                defen.remove(pkmn[new_mon]["STATS"][2])
                spatk.remove(pkmn[new_mon]["STATS"][3])
                spdef.remove(pkmn[new_mon]["STATS"][4])
                spe.remove(pkmn[new_mon]["STATS"][5])

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

                stats2 = json_f[ex]["POKEMON_1"]["STATS"]
                type_effective2 = json_f[ex]["POKEMON_1"]["TYPE_EFFECTIVENESS"]
                type2 = json_f[ex]["POKEMON_1"]["TYPE"]
                utility2 = json_f[ex]["POKEMON_1"]["UTILITY"]

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

                total_weak = 0
                for i in range(len(weak)):
                    temp = weak[i] * (1/(2 * (res[i] + 1/2)))

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
                    if types[i] >= 2 and i != None and i != "None":
                        total_repeat += types[i] - 1
                    
                total_res = 0
                for i in range(len(weak)):

                    if res[i] < 2:
                        total_res += 1

                rocks = 0
                removal = 0
                everything_else = 0
                pivot = 0

                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1
                
                for move in utility2:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
                        pivot += 1
                    else:
                        everything_else += 1

                atk_sp_diff = abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))
                def_sp_diff = abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))
                less_30 = 0
                less_60 = 0
                less_90 = 0
                less_120 = 0
                plus_120 = 0

                for spe_stat in spe:

                    if spe_stat < 30:
                        less_30 += 1
                    elif spe_stat < 60:
                        less_60 += 1
                    elif spe_stat < 90:
                        less_90 += 1
                    elif spe_stat < 120:
                        less_120 += 1
                    else:
                        plus_120 += 1

                stats_1 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, total_weak, total_res, total_unres, total_repeat]
                #print(stats_0)
                #print(stats_1)
                #print(json_f[ex]["Better"])
                #print("------------------------------------------------------------------------")
                
                if json_f[ex]["Better"] == 0:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(0)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(1)
                else:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        with_anno_label.append(stats_0 + stats_1 + [anno_i])
                        labels.append(1)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        with_anno_label.append(stats_1 + stats_0 + [anno_i])
                        labels.append(0)

                anno_i += 1

    np.save("./data/training_processed/" + featureset_name + "_pkmn0_data.npy",np.array(data_0))
    np.save("./data/training_processed/" + featureset_name + "_pkmn1_data.npy",np.array(data_1))
    np.save("./data/training_processed/" + featureset_name + "_combined_data.npy",np.array(combined))
    np.save("./data/training_processed/" + featureset_name + "_combined_annotator_data.npy",np.array(with_anno_label))
    np.save("./data/training_processed/" + featureset_name + "_labels_data.npy",np.array(labels))


def from_json_to_numpy_A_exclude_small_annotators():

    """
    Features Included
    """

    featureset_name = "A"

    pkmn = {}

    data_0 = []
    data_1 = []
    labels = []
    combined = []

    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)

    onlyfiles = [join("./data/cosmog_training_data/", f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    for file in onlyfiles:
        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)
            print(file)

            if len(json_f) < 40:
                continue


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

            for ex in json_f:

                for mon in json_f[ex]["STARTING_TEAM"]:

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
                        if move not in utility and move in utility_moves:
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

                new_utility = []

                new_mon = json_f[ex]["POKEMON_0"]

                for move in pkmn[new_mon]["UTILITY"]:
                    if move not in utility and move in utility_moves:
                        new_utility.append(move)

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

                
                atk_sp_diff = abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))
                def_sp_diff = abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))
                avg_speed = (sum(spe) /len(spe))

                rocks = 0
                removal = 0
                everything_else = 0
                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1
                
                for move in new_utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1

                stats_0 = [atk_sp_diff, def_sp_diff, avg_speed, rocks, removal, everything_else, total_weak, total_res, total_unres, total_repeat]

                stats_1 = []


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

                stats2 = json_f[ex]["POKEMON_1"]["STATS"]
                type_effective2 = json_f[ex]["POKEMON_1"]["TYPE_EFFECTIVENESS"]
                type2 = json_f[ex]["POKEMON_1"]["TYPE"]
                utility2 = json_f[ex]["POKEMON_1"]["UTILITY"]

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

                rocks = 0
                removal = 0
                everything_else = 0

                for move in utility:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1
                
                for move in utility2:
                    if move == "Stealth Rock" and rocks == 0:
                        rocks += 1
                    elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
                        removal += 1
                    else:
                        everything_else += 1

                atk_sp_diff = abs(sum(atk) /len(atk) - sum(spatk) / len(spatk))
                def_sp_diff = abs(sum(defen) /len(defen) - sum(spdef) / len(spdef))
                avg_speed = (sum(spe) /len(spe))

                stats_1 = [atk_sp_diff, def_sp_diff, avg_speed, rocks, removal, everything_else, total_weak, total_res, total_unres, total_repeat]
                #print(stats_0)
                #print(stats_1)
                #print(json_f[ex]["Better"])
                #print("------------------------------------------------------------------------")
                
                if json_f[ex]["Better"] == 0:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        labels.append(0)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        labels.append(1)
                else:
                    if random.random() < 0.5:
                        data_0.append(stats_0)
                        data_1.append(stats_1)
                        combined.append(stats_0 + stats_1)
                        labels.append(1)
                    else:
                        data_0.append(stats_1)
                        data_1.append(stats_0)
                        combined.append(stats_1 + stats_0)
                        labels.append(0)

    np.save("./data/training_processed/small_removed_" + featureset_name + "_pkmn0_data.npy",np.array(data_0))
    np.save("./data/training_processed/small_removed_" + featureset_name + "_pkmn1_data.npy",np.array(data_1))
    np.save("./data/training_processed/small_removed_" + featureset_name + "_combined_data.npy",np.array(combined))
    np.save("./data/training_processed/small_removed_" + featureset_name + "_labels_data.npy",np.array(labels))



def test_small():

    X = np.load("./data/training_processed/A_combined_data.npy")
    y = np.load("./data/training_processed/A_labels_data.npy")

    clf = MLPClassifier(random_state=0).fit(X, y)
    
    print(clf.score(X, y))

    X = np.load("./data/training_processed/small_removed_A_combined_data.npy")
    y = np.load("./data/training_processed/small_removed_A_labels_data.npy")

    clf = MLPClassifier(random_state=0).fit(X, y)
    
    print(clf.score(X, y))



                
def proof_of_concept(featureset = "A"):

    X = np.load("./data/training_processed/"+featureset+"_combined_data.npy")
    y = np.load("./data/training_processed/"+featureset+"_labels_data.npy")

    clf = LogisticRegression(random_state=0).fit(X, y)
    
    print(clf.score(X, y))

    X = np.load("./data/training_processed/"+featureset+"_pkmn0_data.npy") - np.load("./data/training_processed/"+featureset+"_pkmn1_data.npy")
    y = np.load("./data/training_processed/"+featureset+"_labels_data.npy")

    clf = LogisticRegression(random_state=0).fit(X, y)
    
    print(clf.score(X, y))

    X = np.load("./data/training_processed/"+featureset+"_combined_data.npy")
    y = np.load("./data/training_processed/"+featureset+"_labels_data.npy")

    clf = MLPClassifier(random_state=0).fit(X, y)
    
    print(clf.score(X, y))

    X = np.load("./data/training_processed/"+featureset+"_combined_annotator_data.npy")
    y = np.load("./data/training_processed/"+featureset+"_labels_data.npy")

    clf = MLPClassifier(random_state=0).fit(X, y)
    
    print(clf.score(X, y))


def inter_rater_agreement():

    continue_rating = True
    pkmn = {}

    data_0 = []
    data_1 = []
    labels = []
    combined = []

    ratings = {}

    with open("./data/rater_agreement.json", "r") as file:
        ratings = json.load(file)

    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)

    onlyfiles = [join("./data/cosmog_training_data/", f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    while continue_rating:
        new = False
        fname = random.choice(onlyfiles)
        index = 0

        if not ratings["Chosen"].get(fname):

            train_data = {}
            with open(fname, "r") as file:
                    train_data = json.load(file)
            curr_index = int(max(list(map(int, train_data.keys()))))

            index = str(random.randint(0, curr_index))

            ratings["Chosen"][fname] = [index]

        else:
            train_data = {}
            with open(fname, "r") as file:
                    train_data = json.load(file)

            taken_indecies = ratings["Chosen"][fname]
            curr_index = int(max(list(map(int, train_data.keys()))))

            while len(taken_indecies) >= curr_index:
                fname = random.choice(onlyfiles)

                if not ratings["Chosen"].get(fname):
                    
                    new = True
                    train_data = {}
                    with open(fname, "r") as file:
                            train_data = json.load(file)
                    curr_index = int(max(list(map(int, train_data.keys()))))
                    taken_indecies = []

                    index = str(random.randint(0, curr_index))

                    ratings["Chosen"][fname] = [index]

                else:
                    train_data = {}
                    with open(fname, "r") as file:
                            train_data = json.load(file)

                    taken_indecies = ratings["Chosen"][fname]
                    curr_index = int(max(list(map(int, train_data.keys()))))

            if not new:
                index = str(random.randint(0, curr_index))

                while index in ratings["Chosen"][fname]:
                    index = str(random.randint(0, curr_index))

                ratings["Chosen"][fname].append(index)

        json_f = {}
        with open(fname, "r") as file:
            json_f = json.load(file)

            starting_team = json_f[index]["STARTING_TEAM"]
            pkmn_0 = json_f[index]["POKEMON_0"]
            pkmn_1_stats = json_f[index]["POKEMON_1"]["STATS"]
            pkmn_1_type = json_f[index]["POKEMON_1"]["TYPE"]
            pkmn_1_utility = json_f[index]["POKEMON_1"]["UTILITY"]
            pkmn_1_type_effectiveness = json_f[index]["POKEMON_1"]["TYPE_EFFECTIVENESS"]
            better = json_f[index]["Better"]



            current_team_stats = ""
            new_stats_0 = ""
            new_stats_1 = ""
            
            new_mon = pkmn_0

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
                    if move not in utility and move in utility_moves:
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


            stats2 = pkmn_1_stats

            type_list = pkmn_1_type
            type2 = pkmn_1_type


            
            type_effective2 = pkmn_1_type_effectiveness

            utility2 = pkmn_1_utility
            new_utility = []

            for move in pkmn[new_mon]["UTILITY"]:
                if move not in utility:
                    new_utility.append(move)


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
            new_stats_1+=("Utility moves: "+ str(utility2))

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

            print(file)
            print(index)
            print("\n")
            print(current_team_stats)
            print("\n")
            print(new_stats_0)
            print("\n")
            print(new_stats_1)
            print("\n")

            #implement tracking which mon is actually better
            better_2 = input("Which one is better? ")
            ratings["Rated"].append((str(better), better_2, fname))

            with open("./data/rater_agreement.json", "w") as wfile:
                json.dump(ratings,wfile, indent=4)

            stop = input("Continue? 0 or 1: ")

            

            if stop == "0":
                continue_rating = False




def calculate_inter_rater_agreement():

    ratings = {}
    with open("./data/rater_agreement.json", "r") as file:
        ratings = json.load(file)

    agree = 0
    disagree = 0

    for rate in ratings["Rated"]:
        if rate[0] == rate[1]:
            agree += 1
        else:
            disagree += 1

    print("Agreement Percentage:", agree / (agree + disagree))
    print("Number Rated:", agree+disagree)




def make_draft_CV():

    pkmn = {}

    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)

    drafts = pd.read_csv("./data/example_drafts.csv")

    teams = []

    prev_coach = ""
    team_index = -1
    num_mons = 0
    for m in range(drafts.shape[0]):

        mon = drafts.iloc[m]["Pokémon"]
        coach = drafts.iloc[m]["CoachComplete"]

        if coach != prev_coach and mon is not np.nan:
            prev_coach = coach
            team_index+=1
            teams.append([])

        if mon is not np.nan:

            if "(T)" in mon:
                mon = mon.replace(" (T)", "")
            
            if "-Incarnate" in mon:
                mon = mon.replace("-Incarnate", "")

            if "-Single-Strike" in mon:
                mon = mon.replace("-Single-Strike", "")

            if "-Teal" in mon:
                mon = mon.replace("-Teal", "")

            if "-50%" in mon:
                mon = mon.replace("-50%", "")

            if "-Midday" in mon:
                mon = mon.replace("-Midday", "")

            if "Tauros-Paldea" == mon:
                mon = mon.replace("Tauros-Paldea", "Tauros-Paldea-Combat")

            if "Sirfetch" in mon:
                mon = mon.replace("Sirfetch'd","Sirfetchu2019d")

            if "Farfetch" in mon:
                mon = mon.replace("Farfetch'd","Farfetchu2019d")
            
            if "Pan-All" in mon:
                mon = mon.replace("Pan-All","Pansage")

            if "Pan-All" in mon:
                mon = mon.replace("Pan-All","Pansear")
            
            if "Simi-All" in mon:
                mon = mon.replace("Simi-All","Simisear")

            if "Ogerpon-All" in mon:
                mon = mon.replace("Ogerpon-All","Ogerpon")

            if "Tauros-Paldea-All" in mon:
                mon = mon.replace("Tauros-Paldea-All","Tauros-Paldea-Blaze")

            if "Rotom-House" in mon:
                mon = mon.replace("Rotom-House","Rotom-Wash")

            
            if not pkmn.get(mon) and mon not in BANNED:
                print(mon)

            if mon not in BANNED:
                teams[team_index].append(mon)
                num_mons += 1

    #compute one mon drop out teams

    random.shuffle(teams)
    cv_barrier = len(teams) // 5

    cv1 = teams[0:cv_barrier]
    cv2 = teams[cv_barrier:2*cv_barrier]
    cv3 = teams[2*cv_barrier:3*cv_barrier]
    cv4 = teams[3*cv_barrier:4*cv_barrier]
    cv5 = teams[4*cv_barrier:]

    cv1_dropout = []
    cv2_dropout = []
    cv3_dropout = []
    cv4_dropout = []
    cv5_dropout = []

    num_team = 0
    for team in teams:
        for i in range(6):

            if num_team < cv_barrier:
                cv1_dropout.append([team[0:i] + team[i+1:], team[i]])
            elif num_team < 2*cv_barrier:
                cv2_dropout.append([team[0:i] + team[i+1:], team[i]])
            elif num_team < 3*cv_barrier:
                cv3_dropout.append([team[0:i] + team[i+1:], team[i]])
            elif num_team < 4*cv_barrier:
                cv4_dropout.append([team[0:i] + team[i+1:], team[i]])
            else:
                cv5_dropout.append([team[0:i] + team[i+1:], team[i]])
        num_team += 1
    
    with open("./data/teams_cv_1.json", "w") as file:
        json.dump(cv1,file)
    with open("./data/teams_cv_2.json", "w") as file:
        json.dump(cv2,file)
    with open("./data/teams_cv_3.json", "w") as file:
        json.dump(cv3,file)
    with open("./data/teams_cv_4.json", "w") as file:
        json.dump(cv4,file)
    with open("./data/teams_cv_5.json", "w") as file:
        json.dump(cv5,file)

    with open("./data/teams_cv_1_dropout.json", "w") as file:
        json.dump(cv1_dropout,file)
    with open("./data/teams_cv_2_dropout.json", "w") as file:
        json.dump(cv2_dropout,file)
    with open("./data/teams_cv_3_dropout.json", "w") as file:
        json.dump(cv3_dropout,file)
    with open("./data/teams_cv_4_dropout.json", "w") as file:
        json.dump(cv4_dropout,file)
    with open("./data/teams_cv_5_dropout.json", "w") as file:
        json.dump(cv5_dropout,file)


    cv1_probs = {}
    for mon in pkmn:
        cv1_probs[mon] = {}
        for m in pkmn:
            cv1_probs[mon][m] = 1
    
    for team in cv1:
        for mon in team:
            for m in team:
                if m != mon:
                    cv1_probs[mon][m] += 1

    for mon in cv1_probs:
        mon_total = 0
        for m in cv1_probs[mon]:
            mon_total += cv1_probs[mon][m]
        
        for m in cv1_probs[mon]:
            cv1_probs[mon][m] /= mon_total

    cv2_probs = {}
    for mon in pkmn:
        cv2_probs[mon] = {}
        for m in pkmn:
            cv2_probs[mon][m] = 1
    
    for team in cv2:
        for mon in team:
            for m in team:
                if m != mon:
                    cv2_probs[mon][m] += 1

    for mon in cv2_probs:
        mon_total = 0
        for m in cv2_probs[mon]:
            mon_total += cv2_probs[mon][m]
        
        for m in cv2_probs[mon]:
            cv2_probs[mon][m] /= mon_total


    cv3_probs = {}
    for mon in pkmn:
        cv3_probs[mon] = {}
        for m in pkmn:
            cv3_probs[mon][m] = 1
    
    for team in cv3:
        for mon in team:
            for m in team:
                if m != mon:
                    cv3_probs[mon][m] += 1

    for mon in cv3_probs:
        mon_total = 0
        for m in cv3_probs[mon]:
            mon_total += cv3_probs[mon][m]
        
        for m in cv3_probs[mon]:
            cv3_probs[mon][m] /= mon_total


    cv4_probs = {}
    for mon in pkmn:
        cv4_probs[mon] = {}
        for m in pkmn:
            cv4_probs[mon][m] = 1
    
    for team in cv4:
        for mon in team:
            for m in team:
                if m != mon:
                    cv4_probs[mon][m] += 1

    for mon in cv4_probs:
        mon_total = 0
        for m in cv4_probs[mon]:
            mon_total += cv4_probs[mon][m]
        
        for m in cv4_probs[mon]:
            cv4_probs[mon][m] /= mon_total


    cv5_probs = {}
    for mon in pkmn:
        cv5_probs[mon] = {}
        for m in pkmn:
            cv5_probs[mon][m] = 1
    
    for team in cv5:
        for mon in team:
            for m in team:
                if m != mon:
                    cv5_probs[mon][m] += 1

    for mon in cv5_probs:
        mon_total = 0
        for m in cv5_probs[mon]:
            mon_total += cv5_probs[mon][m]
        
        for m in cv5_probs[mon]:
            cv5_probs[mon][m] /= mon_total

    
    pd.DataFrame(cv1_probs).to_csv("./data/cv1_probs.csv")
    pd.DataFrame(cv2_probs).to_csv("./data/cv2_probs.csv")
    pd.DataFrame(cv3_probs).to_csv("./data/cv3_probs.csv")
    pd.DataFrame(cv4_probs).to_csv("./data/cv4_probs.csv")
    pd.DataFrame(cv5_probs).to_csv("./data/cv5_probs.csv")



def handle_bad_data_ENN(feature = "A"):


    X = np.load("./data/training_processed/"+feature+"_combined_data.npy")
    print(X.shape)
    y = np.load("./data/training_processed/"+feature+"_labels_data.npy")

    clf = MLPClassifier(random_state=0).fit(X, y)
    
    print("Pre score:", clf.score(X, y))

    enn = EditedNearestNeighbours(n_neighbors=5, kind_sel="mode")
    X_res, y_res = enn.fit_resample(X, y)

    clf = MLPClassifier(random_state=0).fit(X_res, y_res)
    
    print(X_res.shape)
    print("Post score:", clf.score(X_res, y_res))

    res_list = X_res.tolist()

    excluded_i = []
    for r in range(X.shape[0]):

        if X[r].tolist() not in res_list:
            excluded_i.append(r)

    onlyfiles = [join("./data/cosmog_training_data/", f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    len_dict = {}
    removed_dict = {}
    name = []

    i = 0
    for file in onlyfiles:
        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)

        len_dict[file] = (len(json_f))
        removed_dict[file] = 0
        name.append(file.split("/")[-1].split("_training")[0])

        for j in json_f:
            if i in excluded_i:
                removed_dict[file] += 1
            i+=1

    for f in len_dict:
        print(f, "percent removed:", removed_dict[f] / len_dict[f])

    ex = []
    for x in len_dict:
        ex.append(len_dict[x] - removed_dict[x])

    ex_r = []
    for x in removed_dict:
        ex_r.append(removed_dict[x])


    print(len(excluded_i))

    i = 0
    for file in onlyfiles:
        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)

        len_dict[file] = (len(json_f))
        removed_dict[file] = 0
        name.append(file.split("/")[-1].split("_training")[0])

        pop = []
        for j in json_f:
            if i not in excluded_i:
                pop.append(j)
            i+=1
        
        for j in pop:
            json_f.pop(j)

        if not os.path.exists("./data/no_outlier_training_data_"+feature+"/"):
            os.mkdir("./data/no_outlier_training_data_"+feature+"/")
        file = "./data/no_outlier_training_data_"+feature+"/" + file.split("./data/cosmog_training_data/")[1]
        with open(file, "w") as f:
            json.dump(json_f,f,indent=4)


    plt.figure(figsize=(12, 8))
    sort_i = np.argsort(np.array(ex))
    plt.barh(np.array(name)[sort_i], np.array(ex)[sort_i])
    plt.barh(np.array(name)[sort_i], np.array(ex_r)[sort_i], left= np.array(ex)[sort_i],color="tab:red")
    plt.title("Number of Training Examples Generated by User")
    plt.ylabel("User")
    plt.xlabel("Number of Training Examples")
    plt.yticks(np.array(name)[sort_i],np.array(name)[sort_i],rotation=0, fontsize="7")
    plt.savefig("./data/annotation_removed_plot")
    


def hold_one_out_accuracy():


    X = np.load("./data/training_processed/A_combined_data.npy")
    y = np.load("./data/training_processed/A_labels_data.npy")


    onlyfiles = [join("./data/cosmog_training_data/", f) for f in listdir("./data/cosmog_training_data/") if isfile(join("./data/cosmog_training_data/", f)) and "No_Name_Provided" not in f and "doubles" not in f]

    len_dict = {}
    name = []

    i = 0
    for file in onlyfiles:
        json_f = {}
        with open(file, "r") as f:
            json_f = json.load(f)

        len_dict[file] = (len(json_f))
        name.append(file.split("/")[-1].split("_training")[0])

    
    start_i = 0
    performance_list = []
    for n in name:

        ln = ""
        for l in len_dict:
            if n in l and (n != "Stryfe" or "Stryfe'sFriend" not in l):
                ln = l

        X_test = X[start_i:start_i+len_dict[ln]]
        y_test = y[start_i:start_i+len_dict[ln]]
        X_train = np.concat([X[0:start_i], X[start_i + len_dict[ln]:]])
        y_train = np.concat([y[0:start_i], y[start_i + len_dict[ln]:]])

        clf = MLPClassifier(random_state=0).fit(X_train, y_train)
    
        performance_list.append(clf.score(X_test, y_test))

        start_i += len_dict[l]

    plt.figure(figsize=(12, 8))
    sort_i = np.argsort(np.array(performance_list))
    plt.barh(np.array(name)[sort_i], np.array(performance_list)[sort_i])
    plt.title("Performance of Model With One User Being Held Out")
    plt.ylabel("User")
    plt.xlabel("Performance")
    plt.yticks(np.array(name)[sort_i],np.array(name)[sort_i],rotation=0, fontsize="7")
    plt.savefig("./data/held_performance_plot")

    num_kept = 0
    for i in range(len(performance_list)):
        if performance_list[i] > 0.5:
            for l in len_dict:
                if name[i] in l and (name[i] != "Stryfe" or "Stryfe'sFriend" not in l):
                    num_kept += len_dict[l]

    print(num_kept)



class MLP_1(nn.Module):
    def __init__(self, input_shape):
        super().__init__()
        self.lin0 = nn.Linear(input_shape, 100)
        self.lin1 = nn.Linear(100, 1)
        self.nonlinear = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.nonlinear(self.lin0(x))
        return self.sigmoid(self.lin1(x))
    
class MLP_2(nn.Module):
    def __init__(self, input_shape):
        super().__init__()
        self.lin0 = nn.Linear(input_shape, 10)
        self.lin1 = nn.Linear(10, 1)
        self.nonlinear = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.nonlinear(self.lin0(x))
        return self.sigmoid(self.lin1(x))
    
class MLP_3(nn.Module):
    def __init__(self, input_shape):
        super().__init__()
        self.lin0 = nn.Linear(input_shape, 100)
        self.lin1 = nn.Linear(100, 10)
        self.lin2 = nn.Linear(10, 1)
        self.nonlinear = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.nonlinear(self.lin0(x))
        return self.sigmoid(self.lin2(self.nonlinear(self.lin1(x))))
    

def grid_search():

    ## Training
    epochs=[1000,2000,3000]
    featureset_list = ["A", "B", "C"]
    model_list = [1,2,3]
    lr = [1e-4, 1e-3]

    np.random.seed(42)



    

    test_acc = {}
    ii = 0
    for e in epochs:
        for f in featureset_list:
            for m in model_list:
                for l in lr:

                    X = np.load("./data/training_processed/"+f+"_combined_data.npy").astype(np.float32)
                    y = np.load("./data/training_processed/"+f+"_labels_data.npy").astype(np.float32)
                    np.random.shuffle(X)
                    np.random.shuffle(y)
                    X = torch.from_numpy(X)
                    y = torch.from_numpy(y).view(-1,1)

                    kf = KFold(n_splits=5)
                    kf.get_n_splits(X)

                    KFold(n_splits=5, random_state=None, shuffle=False)
                    
                    splits = kf.split(X)
                    c_total = 0
                    t_total = 0
                    for i, (train_index, test_index) in enumerate(splits):
                        

                        if m == 1:
                            model = MLP_1(len(X[0]))
                        if m == 2:
                            model = MLP_2(len(X[0]))
                        if m == 3:
                            model = MLP_3(len(X[0]))

                        # Loss and Optimizer
                        criterion = nn.BCELoss()
                        optimizer = torch.optim.AdamW(model.parameters(), lr=l, weight_decay=0.0001)

                        # Iterate through train set minibatchs
                        for epoch in range(e):

                            # Zero out the gradients
                            optimizer.zero_grad()
                            
                            # Forward pass
                            pred = model(X[train_index])
                            loss = criterion(pred, y[train_index])
                            # Backward pass
                            loss.backward()
                            optimizer.step()

                        ## Testing
                        correct = 0
                        total = len(X[test_index])

                        with torch.no_grad():
                            # Iterate through test set minibatchs 
                            # Forward pass
                            pred = model(X[test_index])
                            
                            predictions = torch.round(pred)
                            
                            correct += torch.sum((predictions == y[test_index]).float())
                            print(correct)
                        c_total += correct
                        t_total += total
                    print(c_total)
                    print(t_total)
                    print((c_total/t_total).item())
                    test_acc[str(e) + "_" + str(f) + "_" + str(m) + "_" + str(l)] = (c_total/t_total).item()
                    
                    ii+=1
                    print(ii, "/", len(epochs) * len(featureset_list) * len(model_list) * len(lr))
    with open("./data/test_acc.json", "w") as file:
        json.dump(test_acc,file, indent=4)


def train_model(fname = "model.cpt", featureset = "B"):

       ## Training
    epochs=3000
    model_list = 3
    lr = 1e-4

    np.random.seed(42)


    X = np.load("./data/training_processed/"+featureset+"_combined_data.npy").astype(np.float32)
    y = np.load("./data/training_processed/"+featureset+"_labels_data.npy").astype(np.float32)
    np.random.shuffle(X)
    np.random.shuffle(y)
    X = torch.from_numpy(X)
    y = torch.from_numpy(y).view(-1,1)

    kf = KFold(n_splits=5)
    kf.get_n_splits(X)

    KFold(n_splits=5, random_state=None, shuffle=False)
    
        
    model = MLP_3(len(X[0]))

    # Loss and Optimizer
    criterion = nn.BCELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0001)

    # Iterate through train set minibatchs
    for epoch in range(epochs):

        # Zero out the gradients
        optimizer.zero_grad()
        
        # Forward pass
        pred = model(X)
        loss = criterion(pred, y)
        # Backward pass
        loss.backward()
        optimizer.step()

    torch.save(model.state_dict(), "./data/" + fname)



from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import os
from replay_analyze import get_match_stats

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/MBTL_STATS_DB'

from sqlalchemy import event
from sqlalchemy import text
db = SQLAlchemy(app)

def calc_features_one_mon(input_team, input_mon, featureset_name = "B"):
    """
    Features Included
    difference between num phys attackers and spatkers
    difference between num phys defenders and spdefenders
    speed tiers
    rocks
    removal
    pivot
    other utility moves
    weakness score
    resistaqnce score
    unresisted score
    repeated types
    """

    pkmn = {}

    data_0 = []
    data_1 = []
    labels = []
    combined = []
    with_anno_label = []


    with open("./data/Pokemon_Feature_Data.json", "r") as file:
        pkmn = json.load(file)


    atk = 0
    defen = 0
    spatk = 0
    spdef = 0
    spe = []
    weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    num_weak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    res =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    types = {}
    utility = []


    for mon in input_team:

        if pkmn[mon]["STATS"][1] > pkmn[mon]["STATS"][3] *1.3:
            atk += 1
        elif pkmn[mon]["STATS"][1] * 1.3 < pkmn[mon]["STATS"][3]:
            spatk += 1
        else:
            if pkmn[mon]["STATS"][1] >= pkmn[mon]["STATS"][3]:
                atk += 1
            else:
                spatk += 1


        if pkmn[mon]["STATS"][2] > pkmn[mon]["STATS"][4] *1.3:
            defen += 1
        elif pkmn[mon]["STATS"][2] * 1.3 < pkmn[mon]["STATS"][4]:
            spdef += 1
        else:
            if pkmn[mon]["STATS"][2] >= pkmn[mon]["STATS"][4]:
                defen += 1
            else:
                spdef += 1

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
            if move not in utility and move in utility_moves:
                utility.append(move)

    total_weak = 0
    for i in range(len(weak)):
        temp = weak[i] * (1/(2 * (res[i] + 1/2)))

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

    total_weak = 0
    for i in range(len(weak)):
        temp = weak[i] * (1/(2 * (res[i] + 1/2)))

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
        if types[i] >= 2 and i != None and i != "None":
            total_repeat += types[i] - 1
        
    total_res = 0
    for i in range(len(weak)):

        if res[i] < 2:
            total_res += 1

    
    atk_sp_diff = abs(atk - spatk)
    def_sp_diff = abs(defen - spdef)
    less_30 = 0
    less_60 = 0
    less_90 = 0
    less_120 = 0
    plus_120 = 0

    for spe_stat in spe:

        if spe_stat < 30:
            less_30 += 1
        elif spe_stat < 60:
            less_60 += 1
        elif spe_stat < 90:
            less_90 += 1
        elif spe_stat < 120:
            less_120 += 1
        else:
            plus_120 += 1


    rocks = 0
    removal = 0
    pivot = 0
    everything_else = 0
    for move in utility:
        if move == "Stealth Rock" and rocks == 0:
            rocks += 1
        elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
            removal += 1
        elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
            pivot += 1
        else:
            everything_else += 1

    stats_0 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, rocks, removal, pivot, everything_else, total_weak, total_res, total_unres, total_repeat]

    if featureset_name == "D":
        stats_0 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, total_weak**3, total_res, total_unres, total_repeat, rocks, removal]
    
    stats_1 = []

    type2 = [input_mon[0], input_mon[1]]

    stats2 = [float(input_mon[2]), float(input_mon[3]), float(input_mon[4]), float(input_mon[5]), float(input_mon[6]), float(input_mon[7])]
    type_effective2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    if type2[1] == None:
        for i in range(len(WEAKNESS[type2[0]])):
            type_effective2[i] = WEAKNESS[type2[0]][i] * RESISTANCE[type2[0]][i]
    else:
        for i in range(len(WEAKNESS[type2[0]])):
            type_effective2[i] = WEAKNESS[type2[0]][i] * RESISTANCE[type2[0]][i] * WEAKNESS[type2[1]][i] * RESISTANCE[type2[1]][i]

    for move in pkmn[input_mon[-1]]["UTILITY"]:
            if move not in utility and move in utility_moves:
                utility.append(move)

    if stats2[1] > stats2[3] *1.3:
        atk += 1
    elif stats2[1] * 1.3 < stats2[3]:
        spatk += 1
    else:
        if stats2[1] > 100:
            atk += 1
        if stats2[3] > 100:
            spatk += 1

    if stats2[2] > stats2[4] *1.3:
        defen += 1
    elif stats2[2] * 1.3 < stats2[4]:
        spdef += 1
    else:
        if stats2[2] > 100:
            defen += 1
        if stats2[4] > 100:
            spdef += 1
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

    total_weak = 0
    for i in range(len(weak)):
        temp = weak[i] * (1/(2 * (res[i] + 1/2)))

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
        if types[i] >= 2 and i != None and i != "None":
            total_repeat += types[i] - 1
        
    total_res = 0
    for i in range(len(weak)):

        if res[i] < 2:
            total_res += 1

    rocks = 0
    removal = 0
    everything_else = 0
    pivot = 0

    for move in utility:
        if move == "Stealth Rock" and rocks == 0:
            rocks += 1
        elif (move == "Defog" or move == "Rapid Spin") and removal == 0:
            removal += 1
        elif (move == "Baton Pass" or move == "U-Turn") and removal == 0:
            pivot += 1
        else:
            everything_else += 1

    atk_sp_diff = abs(atk - spatk)
    def_sp_diff = abs(defen - spdef)
    less_30 = 0
    less_60 = 0
    less_90 = 0
    less_120 = 0
    plus_120 = 0

    for spe_stat in spe:

        if spe_stat < 30:
            less_30 += 1
        elif spe_stat < 60:
            less_60 += 1
        elif spe_stat < 90:
            less_90 += 1
        elif spe_stat < 120:
            less_120 += 1
        else:
            plus_120 += 1

    stats_1 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, rocks, removal, pivot, everything_else, total_weak, total_res, total_unres, total_repeat]
    if featureset_name == "D":
        stats_1 = [atk_sp_diff, def_sp_diff, less_30, less_60, less_90, less_120, plus_120, total_weak**3, total_res, total_unres, total_repeat, rocks, removal]
    
    #print(stats_0)
    #print(stats_1)
    #print(json_f[ex]["Better"])
    #print("------------------------------------------------------------------------")
    
    return stats_0 + stats_1
    

def get_ranking(model, input_team = [], pokemon_list = [], f = "B"):

    scores = []

    with app.app_context():
        connection = db.session.connection()

        names = []
        ###### UPDATE THIS SO THAT QUERY ONLY GETS MON IN MON LIST
        result = connection.execute( text(f"""SELECT type1,type2,HP,ATK,DEF,SPATK,SPDEF,SPE, pkmn_name from PKMN_Stats""") )
        for row in result:
            if pokemon_list[row[-1]]:
                features = calc_features_one_mon(input_team, row, f)
                score = model(torch.from_numpy(np.array(features).astype(np.float32))).item()
                scores.append(score)
                names.append(str(row[-1]))

    sort_i = np.argsort(np.array(scores))
    sorted_mons = np.array(names)[sort_i]

    print(np.array(scores)[sort_i][0])
    print(np.array(names)[sort_i][0])
    print(np.array(scores)[sort_i][-1])
    print(np.array(names)[sort_i][-1])

    return sorted_mons

def get_ranking_linear(model, input_team = [], pokemon_list = [], f = "B"):

    scores = []
    names = []

    with app.app_context():
        connection = db.session.connection()

        ###### UPDATE THIS SO THAT QUERY ONLY GETS MON IN MON LIST
        result = connection.execute( text(f"""SELECT type1,type2,HP,ATK,DEF,SPATK,SPDEF,SPE, pkmn_name from PKMN_Stats""") )
        for row in result:
            if pokemon_list[row[-1]]:
                features = calc_features_one_mon(input_team, row, f)
                difference_features = np.array(features[0:13]) - np.array(features[13:])
                weights = np.array([-0.5,-0.5,-2.5,-2,-1.5,-1,-1, -0.3, 3, -0.2, -20, 10 , 7])
                score = nn.Sigmoid()(torch.sum(torch.from_numpy(difference_features) * torch.from_numpy(weights)))
                scores.append(score)
                names.append(str(row[-1]))

    sort_i = np.argsort(np.array(scores))
    sorted_mons = np.array(names)[sort_i]

    
    return sorted_mons


def test_ranking(input_team = [], model_name = "model.cpt", model_shape = 30, f= "B", dumb="True"):

    model =  MLP_3(model_shape)
    model.load_state_dict(torch.load("./data/" + model_name, weights_only=True))
    model.eval()

    learnsets = {}
    with open("Pokemon_Info/learnsets.json") as moves:
        learnsets = json.load(moves)

    pokemon_list = {}
    with app.app_context():
        connection = db.session.connection()
        result = connection.execute( text(f"""SELECT type1,type2,HP,ATK,DEF,SPATK,SPDEF,SPE, pkmn_name from PKMN_Stats""") )
        for row in result:
            include = True
            if row[8] in BANNED:
                include = False

            if row[8] in input_team:
                include = False

            if int(row[2]) + int(row[3]) + int(row[4]) + int(row[5]) + int(row[6]) + int(row[7]) < 440:
                include = False


            pokemon_list[row[-1]] = include                

            
    if dumb:
        ranked = get_ranking_linear(model, input_team, pokemon_list, f)
    else:
        ranked = get_ranking(model, input_team, pokemon_list, f)[::-1]
    for i in ranked[0:10]:
        print(i)
    return ranked[0:10]

def five_fold_impute():

    cv1 = {}
    with open("./data/teams_cv_1_dropout.json", "r") as file:
        cv1 = json.load(file)

    cv2 = {}
    with open("./data/teams_cv_2_dropout.json", "r") as file:
        cv2 = json.load(file)

    cv3 = {}
    with open("./data/teams_cv_3_dropout.json", "r") as file:
        cv3 = json.load(file)

    cv4 = {}
    with open("./data/teams_cv_4_dropout.json", "r") as file:
        cv4 = json.load(file)

    cv5 = {}
    with open("./data/teams_cv_5_dropout.json", "r") as file:
        cv5 = json.load(file)

    cv1_p = pd.read_csv("./data/cv1_probs.csv", index_col=0)
    cv2_p = pd.read_csv("./data/cv1_probs.csv", index_col=0)
    cv3_p = pd.read_csv("./data/cv1_probs.csv", index_col=0)
    cv4_p = pd.read_csv("./data/cv1_probs.csv", index_col=0)
    cv5_p = pd.read_csv("./data/cv1_probs.csv", index_col=0)

    pokemon_list = []
    with app.app_context():
        connection = db.session.connection()
        result = connection.execute( text(f"""SELECT type1,type2,HP,ATK,DEF,SPATK,SPDEF,SPE, pkmn_name from PKMN_Stats""") )
        for row in result:
            include = True
            if row[8] in BANNED:
                include = False

            if int(row[2]) + int(row[3]) + int(row[4]) + int(row[5]) + int(row[6]) + int(row[7]) < 440:
                include = False

            if include:
                pokemon_list.append(row[-1])   

    for team in cv1:

        true = team[1]

        prob = []
        names = []
        for mon in pokemon_list:
            p = 1
            for mon2 in team[0]:
                p *= cv1_p[mon][mon2]
            names.append(mon)
            prob.append(p)

        sort_i = np.argsort(np.array(prob))
        sort_names = np.array(names)[sort_i]

        print("********************")
        print(np.array(prob)[sort_i][0:10])
        print(np.array(prob)[sort_i][-10:])

    



if __name__ == "__main__":
    #count_examples()
    #training_plot()
    #from_json_to_numpy_A("./data/cosmog_training_data/")
    #from_json_to_numpy_A()
    #proof_of_concept()
    #inter_rater_agreement()
    #calculate_inter_rater_agreement()
    #make_draft_CV()
    #handle_bad_data_ENN() # can be seen as exluding each annotator's most egregious examples of personal preference seeping into the data
    #from_json_to_numpy_A_exclude_small_annotators()
    #test_small() # get rid of smaller annotators that may introduce variance into the model
    #hold_one_out_accuracy()
    #from_json_to_numpy_B("./data/cosmog_training_data/")
    #handle_bad_data_ENN("B") 
    #from_json_to_numpy_B()
    #proof_of_concept("B")
    #from_json_to_numpy_C("./data/cosmog_training_data/")
    #handle_bad_data_ENN("C") 
    #from_json_to_numpy_C()
    #proof_of_concept("C")
    #from_json_to_numpy_D("./data/cosmog_training_data/")
    #handle_bad_data_ENN("D") 
    #from_json_to_numpy_D()
    #proof_of_concept("D")
    #grid_search()
    #train_model(fname = "model.cpt", featureset = "B")
    #test_ranking(["Goodra"], model_name = "model_simple.cpt", model_shape = 30)
    #train_model(fname = "model_simple.cpt", featureset = "D")
    #team = ["Goodra", "Gliscor"]
    #for i in range(7):
    #    best = test_ranking(team, model_name = "model_simple.cpt", model_shape = 22, f="D",dumb=True)
    #    team.append(str(best[0]))
    #print(team)
    #five_fold_impute()
    #test_ranking(["Gliscor", "Salamence", "Hydreigon"],model_name = "model.cpt", model_shape = 30, f="B",dumb=False)
    team = ["Goodra", "Gliscor"]
    for i in range(7):
        best = test_ranking(team, model_name = "model.cpt", model_shape = 30, f="B",dumb=False)
        team.append(str(best[0]))
    print(team)

    pass