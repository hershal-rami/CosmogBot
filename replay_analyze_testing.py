import requests
import json

def get_battle_log(link):
    result = requests.get(link)
    source = result.content
    #print(source)
    json_ver = json.loads(source)
    json_ver["log"] = json_ver["log"].split("\n")

    battle_log = (("\n").join(json_ver["log"])).split("|\n|upkeep\n")
    for line in battle_log:
        print("----------------------------------------------------")
        print(line)

    return battle_log

def analyze_log(log):
    print("**************************************************")
    battle_record = {"Status": {}, "Hazards": {}}
    poke_stats = {}
    player_stats = {}

    gen_info = log[0].split("|start")[0]

    p1 = gen_info.split("|player|p1|")[1].split("|")[0]
    p2 = gen_info.split("|player|p2|")[1].split("|")[0]

    print(p1, p2)

    battle_record["p1"] = {"SD user": p1, "Pokemon": {}, "Pokemon Remaining": []}
    battle_record["p2"] = {"SD user": p2, "Pokemon": {}, "Pokemon Remaining": []}

    player_stats[p1] = {"Pokemon Used": []}
    player_stats[p2] = {"Pokemon Used": []}

    for poke in gen_info.split("|poke|p1|")[1:7]:

        poke = poke.split(",")[0].split("|")[0]

        battle_record["p1"]["Pokemon"][poke] = {"Percent": 100, "Status": "None", "Kills": 0, "Dead": False}
        battle_record["p1"]["Pokemon Remaining"].append([poke])
        poke_stats[poke] = {"Lead": False, "Moves Used": {}, "Damage Taken": 0, "Damage Dealt": 0}
        player_stats[p1]["Pokemon Used"].append(poke)

    for poke in gen_info.split("|poke|p2|")[1:7]:

        poke = poke.split(",")[0].split("|")[0]

        battle_record["p1"]["Pokemon"][poke] = {"Percent": 100, "Status": "None", "Kills": 0, "Dead": False}
        battle_record["p1"]["Pokemon Remaining"].append([poke])
        poke_stats[poke] = {"Lead": False, "Moves Used": {}, "Damage Taken": 0, "Damage Dealt": 0}
        player_stats[p2]["Pokemon Used"].append(poke)

    print(battle_record)
    print(poke_stats)
    print(player_stats)

    start = log[0].split("|start")[1]

    battle_record

    p1_curr_mon = {"Name": "", "Nickname": ""}
    p2_curr_mon = {"Name": "", "Nickname": ""}

    p1_curr_mon["Name"] = start.split("|switch|p1a: ")[1].split("|")[1].split(",")[0].split("|")[0]
    p2_curr_mon["Name"] = start.split("|switch|p2a: ")[1].split("|")[1].split(",")[0].split("|")[0]

    p1_curr_mon["Nickname"] = start.split("|switch|p1a: ")[0]
    p2_curr_mon["Nickname"] = start.split("|switch|p2a: ")[0]

    poke_stats[p1_curr_mon]["Lead"] = True
    poke_stats[p2_curr_mon]["Lead"] = True

    turn1 = log[0].split("|turn|1")[1]

    if(turn1.contains("|switch|p1a:")):
        p1_curr_mon["Name"] = turn1.split("|switch|p1a: ")[1].split["|"][1].split("|")[1].split(",")[0].split("|")[0]
        p1_curr_mon["Nickname"] = turn1.split("|switch|p1a: ")[0]
        battle_record["p1"]["Pokemon"][p1_curr_mon]["Percent"] = turn1.split("|switch|p1a:")[1].split["|"][-1].split["/"][0]

    if(turn1.contains("|switch|p2a:")):
        p2_curr_mon["Name"] = turn1.split("|switch|p2a: ")[1].split["|"][1].split("|")[1].split(",")[0].split("|")[0]
        battle_record["p2"]["Pokemon"][p2_curr_mon]["Percent"] = turn1.split("|switch|p2a:")[1].split["|"][-1].split["/"][0]

    if(turn1.contains("|move|p1a: ")):
        move_name = turn1.split("|move|p1a: ")[1].split("|")[1]
        poke_stats[p1_curr_mon["Name"]]["Moves Used"][move_name] = 1




if __name__ == "__main__":
    replay = "https://replay.pokemonshowdown.com/sports-gen8nationaldexdraft-731995.json"
    analyze_log(get_battle_log(replay))
