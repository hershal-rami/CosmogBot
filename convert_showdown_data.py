import json
"""
The only purpose of this file is to take the learnsets.ts and pokedex.ts file from the pokemon
showdown github and transform it into a json object which can be loaded at a 
later date.
"""

def convert_learnsets():
    learnsets = {}
    with open("Pokemon_Info/learnsets.ts", "r") as moves:
        move_string = moves.read()

        for i in range(1, len(move_string.split("learnset: {")) - 2):

            poke_name = move_string.split("learnset: {")[i].split("},")[-1].split(": {")[0].strip()
            learnsets[poke_name] = []
            for j in range(len((move_string.split("learnset: {")[i+1]).split("},")[0].split(": ["))-1):
                learnsets[poke_name].append((move_string.split("learnset: {")[i+1]).split("},")[0].split(": [")[j].split("],")[-1].strip())

    with open("Pokemon_Info/learnsets.json","w") as learnset_file:
        json.dump(learnsets,learnset_file,indent=4)

def convert_evos():
    evos = {}
    with open("Pokemon_Info/pokedex.ts", "r") as dex_f:
        dex = dex_f.read()
        dex = dex.split("SpeciesData} = {\n")[1]
        dex = dex.split(": {\n")
        
        for i in range(len(dex) - 1):
            mon = dex[i].split("\n")[-1].strip()
            evo = dex[i+1].split("evos: ")
            if len(evo) > 1:
                evo = evo[1]
                evo = evo.split("],")[0]
                evos[mon] = []
                for j in evo.split(","):
                    evos[mon].append(remove_non_alpha(j.strip("[").strip(" \"")))



    with open("Pokemon_Info/evos.json","w") as evos_file:
        json.dump(evos,evos_file,indent=4)

def remove_non_alpha(input_str):
    output_str = (''.join([i for i in input_str if i.isalnum()])).lower()
    return output_str

def combine_prevo_moves():
    #adds move from prevo mons to their evolved forms
    evos = {}
    with open("Pokemon_Info/evos.json","r") as evos_file:
        evos = json.load(evos_file)

    learnsets = {}
    with open("Pokemon_Info/learnsets.json","r") as learnset_file:
        learnsets = json.load(learnset_file)

    for mon in evos:
        for evo in evos[mon]:
            if evo in learnsets and mon in learnsets:
                for move in learnsets[mon]:
                    if move not in learnsets[evo]:
                        learnsets[evo].append(move)
                        
    with open("Pokemon_Info/learnsets.json","w") as learnset_file:
        json.dump(learnsets,learnset_file,indent=4)


if __name__ == "__main__":

    #convert_learnsets()
    #convert_evos()
    combine_prevo_moves()

        