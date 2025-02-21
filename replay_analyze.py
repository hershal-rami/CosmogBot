import requests
import json

RESTRICT_MOVE_CHECKING = ["ditto", "smeargle"]

def get_battle_log(link):
    if link[-3:] == "?p2":
        link = link[:-3]
    link = link + ".json"
    result = requests.get(link)
    source = result.content
    #print(source)
    json_ver = json.loads(source)
    json_ver["log"] = json_ver["log"].split("\n")

    battle_log = (("\n").join(json_ver["log"])).split("|turn|")
    #for line in battle_log:
    #    print("----------------------------------------------------")
    #    print(line)

    return battle_log

def get_teams(log):
    turn0 = log[0]
    p1 = turn0.split("p1|")[1].split("|")[0]
    p2 = turn0.split("p2|")[1].split("|")[0]

    game_state = {p1:{}, p2:{}}

    turn0_split = log[0].split("\n")

    p1_mons = []
    for line in turn0_split:

        if "|poke|p1|" in line:

            if "," in line:
                p1_mons.append(line.split("p1|")[1].split(",")[0])
            else:
                p1_mons.append(line.split("p1|")[1].split("|")[0])


    p2_mons = []
    for line in turn0_split:

        if "|poke|p2|" in line:

            if "," in line:
                p2_mons.append(line.split("p2|")[1].split(",")[0])
            else:
                p2_mons.append(line.split("p2|")[1].split("|")[0])

    for mon in p1_mons:
        game_state[p1][mon] = {"Kills":0, "Deaths":0, "HP":100}

    for mon in p2_mons:
        game_state[p2][mon] = {"Kills":0, "Deaths":0,"HP":100}

    return game_state, p1, p2, p1_mons, p2_mons


def get_leads(log, game_state):

    pregame = log[0].split("|turn|1")[0]
    p1_active = pregame.split("|switch|p1a:")[1].split("|")[1]

    if "," in p1_active:
        p1_active = p1_active.split(",")[0]

    p2_active = pregame.split("|switch|p2a:")[1].split("|")[1]

    if "," in p2_active:
        p2_active = p2_active.split(",")[0]

    p1_active_nick = pregame.split("|switch|p1a: ")[1].split("|")[0]

    p2_active_nick = pregame.split("|switch|p2a: ")[1].split("|")[0]

    if "," in p2_active:
        p2_active = p2_active.split(",")[0]

    game_state["p1_active"] = p1_active
    game_state["p2_active"] = p2_active

    game_state["p1_active_nick"] = p1_active_nick
    game_state["p2_active_nick"] = p2_active_nick



def switch(stats_dict,game_state, p1, p2, p1_mons, p2_mons, game_actions, i,turn_num):
    
    if("|switch|p2a" in game_actions[i]):

        if turn_num != 1:
            stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Switched_out"] += 1

        p2_active = game_actions[i].split("|switch|p2a:")[1].split("|")[1]

        if "," in p2_active:
            p2_active = p2_active.split(",")[0]

        p2_active_nick = game_actions[i].split("|switch|p2a: ")[1].split("|")[0]

        game_state["p2_active"] = p2_active
        game_state["p2_active_nick"] = p2_active_nick
        game_state["Nicknames"][p2_active_nick] = p2_active

        #for pokemon with special forms, cahnge it in the state on switch in
        if p2_active not in game_state[p2]:

            remove_mon = ""
            for mon in game_state[p2]:

                if mon[0:3] == p2_active[0:3]:
                    remove_mon = mon

            if remove_mon:
                new_stat_dict = {}
                for stat in stats_dict[p2]["Pokemon"][remove_mon]:
                    new_stat_dict[stat] = stats_dict[p2]["Pokemon"][remove_mon][stat]

                del stats_dict[p2]["Pokemon"][remove_mon]

                stats_dict[p2]["Pokemon"][p2_active] = new_stat_dict

                game_state[p2][p2_active] = {"Deaths": game_state[p2][remove_mon]["Deaths"], "Kills" : game_state[p2][remove_mon]["Kills"]}
                game_state[p2].pop(remove_mon)
                p2_mons.remove(remove_mon)
                p2_mons.append(p2_active)
        
        if "from" not in (game_actions[i].split("|")[-1].split("/")[0]):
            game_state[p2][game_state["p2_active"]]["HP"] = int(game_actions[i].split("|")[-1].split("/")[0])
        else:
            game_state[p2][game_state["p2_active"]]["HP"] = int(game_actions[i].split("|")[-2].split("/")[0])

    if "|drag|p2a" in game_actions[i]:

        if turn_num != 1:
            stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Switched_out"] += 1

        p2_active = game_actions[i].split("|drag|p2a:")[1].split("|")[1]

        if "," in p2_active:
            p2_active = p2_active.split(",")[0]

        p2_active_nick = game_actions[i].split("|drag|p2a: ")[1].split("|")[0]

        game_state["p2_active"] = p2_active
        game_state["p2_active_nick"] = p2_active_nick
        game_state["Nicknames"][p2_active_nick] = p2_active

        #for pokemon with special forms, cahnge it in the state on switch in
        if p2_active not in game_state[p2]:

            remove_mon = ""
            for mon in game_state[p2]:

                if mon[0:3] == p2_active[0:3]:
                    remove_mon = mon

            if remove_mon:
                new_stat_dict = {}
                for stat in stats_dict[p2]["Pokemon"][remove_mon]:
                    new_stat_dict[stat] = stats_dict[p2]["Pokemon"][remove_mon][stat]

                del stats_dict[p2]["Pokemon"][remove_mon]

                stats_dict[p2]["Pokemon"][p2_active] = new_stat_dict

                game_state[p2][p2_active] = {"Deaths": game_state[p2][remove_mon]["Deaths"], "Kills" : game_state[p2][remove_mon]["Kills"]}
                game_state[p2].pop(remove_mon)
                p2_mons.remove(remove_mon)
                p2_mons.append(p2_active)
        
        if "from" not in (game_actions[i].split("|")[-1].split("/")[0]):
            game_state[p2][game_state["p2_active"]]["HP"] = int(game_actions[i].split("|")[-1].split("/")[0])
        else:
            game_state[p2][game_state["p2_active"]]["HP"] = int(game_actions[i].split("|")[-2].split("/")[0])

        
    if"|drag|p1a" in game_actions[i]:

        if turn_num != 1:
            stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Switched_out"] += 1

        p1_active = game_actions[i].split("|drag|p1a:")[1].split("|")[1]

        if "," in p1_active:
            p1_active = p1_active.split(",")[0]

        p1_active_nick = game_actions[i].split("|drag|p1a: ")[1].split("|")[0]

        game_state["p1_active"] = p1_active
        game_state["p1_active_nick"] = p1_active_nick
        game_state["Nicknames"][p1_active_nick] = p1_active

        #for pokemon with special forms, cahnge it in the state on switch in
        if p1_active not in game_state[p1]:

            remove_mon = ""
            for mon in game_state[p1]:

                if mon[0:3] == p1_active[0:3]:
                    remove_mon = mon

            if remove_mon:
                new_stat_dict = {}
                for stat in stats_dict[p1]["Pokemon"][remove_mon]:
                    new_stat_dict[stat] = stats_dict[p1]["Pokemon"][remove_mon][stat]

                del stats_dict[p1]["Pokemon"][remove_mon]

                stats_dict[p1]["Pokemon"][p1_active] = new_stat_dict

                game_state[p1][p1_active] = {"Deaths": game_state[p1][remove_mon]["Deaths"], "Kills" : game_state[p1][remove_mon]["Kills"]}
                game_state[p1].pop(remove_mon)
                p1_mons.remove(remove_mon)
                p1_mons.append(p1_active)
        
        if "from" not in (game_actions[i].split("|")[-1].split("/")[0]):
            game_state[p1][game_state["p1_active"]]["HP"] = int(game_actions[i].split("|")[-1].split("/")[0])
        else:
            game_state[p1][game_state["p1_active"]]["HP"] = int(game_actions[i].split("|")[-2].split("/")[0])


    if("|switch|p1a" in game_actions[i]):

        if turn_num != 1:
            stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Switched_out"] += 1

        p1_active = game_actions[i].split("|switch|p1a:")[1].split("|")[1]

        if "," in p1_active:
            p1_active = p1_active.split(",")[0]

        p1_active_nick = game_actions[i].split("|switch|p1a: ")[1].split("|")[0]

        game_state["p1_active"] = p1_active
        game_state["p1_active_nick"] = p1_active_nick
        game_state["Nicknames"][p1_active_nick] = p1_active

        #for pokemon with special forms,change it in the state on switch in
        if p1_active not in game_state[p1]:

            remove_mon = ""
            for mon in game_state[p1]:

                if mon[0:3] == p1_active[0:3]:
                    remove_mon = mon
                    
            if remove_mon:
                new_stat_dict = {}
                for stat in stats_dict[p1]["Pokemon"][remove_mon]:
                    new_stat_dict[stat] = stats_dict[p1]["Pokemon"][remove_mon][stat]

                del stats_dict[p1]["Pokemon"][remove_mon]

                stats_dict[p1]["Pokemon"][p1_active] = new_stat_dict

                game_state[p1][p1_active] = {"Deaths": game_state[p1][remove_mon]["Deaths"], "Kills" : game_state[p1][remove_mon]["Kills"]}
                game_state[p1].pop(remove_mon)
                p1_mons.remove(remove_mon)
                p1_mons.append(p1_active)

        if "from" not in (game_actions[i].split("|")[-1].split("/")[0]):
            game_state[p1][game_state["p1_active"]]["HP"] = int(game_actions[i].split("|")[-1].split("/")[0])
        else:
            game_state[p1][game_state["p1_active"]]["HP"] = int(game_actions[i].split("|")[-2].split("/")[0])
        
        



def kd_attribution(game_state, p1, p2, game_actions, i):
    
    #check the previous line for other causes of death
    if "fnt|[from] Sandstorm" in game_actions[i-1]:
        
        if "-damage|p1a" in game_actions[i-1]:
            game_state[p1][game_state["p1_active"]]["Deaths"] = 1

            if game_state["Sandstorm"]["Set_by"] in game_state[p1]:
                game_state[p1][game_state["Sandstorm"]["Set_by"]]["Kills"] += 1
            else:
                game_state[p2][game_state["Sandstorm"]["Set_by"]]["Kills"] += 1

        elif "-damage|p2a" in game_actions[i-1]:
            game_state[p2][game_state["p2_active"]]["Deaths"] = 1

            if game_state["Sandstorm"]["Set_by"] in game_state[p1]:
                game_state[p1][game_state["Sandstorm"]["Set_by"]]["Kills"] += 1
            else:
                game_state[p2][game_state["Sandstorm"]["Set_by"]]["Kills"] += 1

    elif "fnt|[from] Stealth Rock" in game_actions[i-1]:
        
        if "-damage|p1a" in game_actions[i-1]:
            game_state[p1][game_state["p1_active"]]["Deaths"] = 1
            game_state[p2][game_state["Rocks"]["p1_side_set_by"]]["Kills"] += 1

        elif "-damage|p2a" in game_actions[i-1]:
            game_state[p2][game_state["p2_active"]]["Deaths"] = 1
            game_state[p1][game_state["Rocks"]["p2_side_set_by"]]["Kills"] += 1

    elif "fnt|[from] Spikes" in game_actions[i-1]:
        
        if "-damage|p1a" in game_actions[i-1]:
            game_state[p1][game_state["p1_active"]]["Deaths"] = 1
            game_state[p2][game_state["Spikes"]["p1_side_set_by"]]["Kills"] += 1

        elif "-damage|p2a" in game_actions[i-1]:
            game_state[p2][game_state["p2_active"]]["Deaths"] = 1
            game_state[p1][game_state["Spikes"]["p2_side_set_by"]]["Kills"] += 1

    elif "fnt|[from] psn" in game_actions[i-1]:
        
        if "-damage|p1a" in game_actions[i-1]:
            game_state[p1][game_state["p1_active"]]["Deaths"] = 1

            if "Zoroark" in game_state["p1_active"] or "Zorua" in game_state["p1_active"]:
                game_state[p2][game_state["p2_active"]]["Kills"] += 1
                return

            if game_state[p2][game_state["Toxic"]["On_p1"][game_state["p1_active"]]["Set_by"]] == "Toxic Orb":
                game_state[p2][game_state["p2_active"]]["Kills"] += 1
            else:
                game_state[p2][game_state["Toxic"]["On_p1"][game_state["p1_active"]]["Set_by"]]["Kills"] += 1

        elif "-damage|p2a" in game_actions[i-1]:
            game_state[p2][game_state["p2_active"]]["Deaths"] = 1

            if "Zoroark" in game_state["p2_active"] or "Zorua" in game_state["p2_active"]:
                game_state[p1][game_state["p1_active"]]["Kills"] += 1
                return

            if game_state[p1][game_state["Toxic"]["On_p2"][game_state["p2_active"]]["Set_by"]] == "Toxic Orb":
                game_state[p1][game_state["p1_active"]]["Kills"] += 1
            else:
                game_state[p1][game_state["Toxic"]["On_p2"][game_state["p2_active"]]["Set_by"]]["Kills"] += 1

    elif "fnt|[from] brn" in game_actions[i-1]:
        
        if "-damage|p1a" in game_actions[i-1]:
            game_state[p1][game_state["p1_active"]]["Deaths"] = 1

            if game_state[p2][game_state["Burn"]["On_p1"][game_state["p1_active"]]["Set_by"]] == "Flame Orb":
                game_state[p2][game_state["p2_active"]]["Kills"] += 1
            else:
                game_state[p2][game_state["Burn"]["On_p1"][game_state["p1_active"]]["Set_by"]]["Kills"] += 1

        elif "-damage|p2a" in game_actions[i-1]:
            game_state[p2][game_state["p2_active"]]["Deaths"] = 1

            if game_state[p1][game_state["Burn"]["On_p2"][game_state["p2_active"]]["Set_by"]] == "Flame Orb":
                game_state[p1][game_state["p1_active"]]["Kills"] += 1
            else:
                game_state[p1][game_state["Burn"]["On_p2"][game_state["p2_active"]]["Set_by"]]["Kills"] += 1


    #fall back case, the kill goes to the mon currently active
    else:
        if "|faint|p2a" in game_actions[i]:
            game_state[p2][game_state["p2_active"]]["Deaths"] = 1

            game_state[p1][game_state["p1_active"]]["Kills"] += 1

        elif "|faint|p1a" in game_actions[i]:
            game_state[p1][game_state["p1_active"]]["Deaths"] = 1

            game_state[p2][game_state["p2_active"]]["Kills"] += 1

def get_string_output(game_state, p1, p2, p1_mons, p2_mons, log):

    line_width = 60
    output = "Match Results\n||```\n"

    p1_survivors = len(p1_mons)
    for pokemon in game_state[p1]:
        if game_state[p1][pokemon]["Deaths"] >= 1:
            p1_survivors -= 1

    p2_survivors = len(p2_mons)
    for pokemon in game_state[p2]:
        if game_state[p2][pokemon]["Deaths"] >= 1:
            p2_survivors -= 1

    if p1_survivors > p2_survivors:
        p1_half = ("W " + p1).ljust(line_width //2 - 4)
        p2_half = (p2 + " L").rjust(line_width //2 - 4)

        if (len(p1_half + p2_half) %2 == 1):
            line1 = (p1_half + " " + str(p1_survivors) + " vs " + str(p2_survivors) + " " + p2_half).center(line_width)
        else:
            line1 = (p1_half + " " + str(p1_survivors) + " vs " + str(p2_survivors) + " " + p2_half).center(line_width - 3)
    else:
        p1_half = ("L " + p1).rjust(len(p2))
        p2_half = (p2 + " W").ljust(len(p1))

        if (len(p1_half + p2_half) %2 == 1):
            line1 = (p1_half + " " + str(p1_survivors) + " vs " + str(p2_survivors) + " " + p2_half).center(line_width)
        else:
            line1 = (p1_half + " " + str(p1_survivors) + " vs " + str(p2_survivors) + " " + p2_half).center(line_width - 3)

    output+=line1+"\n"
    output += "-" * line_width + "\n"
    line2 = "Pokemon K D vs K D Pokemon".center(line_width)
    output+= line2+"\n"
    output += "-" * line_width + "\n"

    for i in range(0,6):
        line = ""

        #just in case they dont bring 6
        if(len(p1_mons) > i):
            p1_line = p1_mons[i].rjust(line_width//2-6) + " " +str(game_state[p1][p1_mons[i]]["Kills"]) + " " + str(game_state[p1][p1_mons[i]]["Deaths"])
        else:
            p1_line = " ".rjust(line_width//2-6) + " " + " "+ " " + " "
        
        if (len(p2_mons) > i):
            p2_line = str(game_state[p2][p2_mons[i]]["Kills"]) + " " + str(game_state[p2][p2_mons[i]]["Deaths"]) + " " + p2_mons[i].ljust(line_width//2-6) 
        else:
            p2_line = "    ".ljust(line_width//2-6)
        
        line = p1_line + "    " + p2_line
        output += line + "\n"

    output+="```||"

    return output

def replace_pokemon(game_state, p1, p2, game_actions, i):

    if("|replace|p2a" in game_actions[i]):

        p2_active = game_actions[i].split("|replace|p2a:")[1].split("|")[1]

        if "," in p2_active:
            p2_active = p2_active.split(",")[0]

        p2_active_nick = game_actions[i].split("|replace|p2a: ")[1].split("|")[0]

        game_state["p2_active"] = p2_active
        game_state["p2_active_nick"] = p2_active_nick
        game_state["Nicknames"][p2_active_nick] = p2_active

    if("|replace|p1a" in game_actions[i]):

        p1_active = game_actions[i].split("|replace|p1a:")[1].split("|")[1]

        if "," in p1_active:
            p1_active = p1_active.split(",")[0]

        p1_active_nick = game_actions[i].split("|replace|p1a: ")[1].split("|")[0]

        game_state["p1_active"] = p1_active
        game_state["p1_active_nick"] = p1_active_nick
        game_state["Nicknames"][p1_active_nick] = p1_active



def set_state(game_state):
    game_state["Toxic"] = {"On_p1": {}, "On_p2":{}}
    game_state["Burn"] = {"On_p1": {}, "On_p2":{}}
    game_state["Sandstorm"] = {"Is_active": False, "Set_by": None}
    game_state["Rocks"] = {"p1_side_is_active": False, "p1_side_set_by": None, "p2_side_is_active": False, "p2_side_set_by": None}
    game_state["Spikes"] = {"p1_side_is_active": False, "p1_side_set_by": None, "p2_side_is_active": False, "p2_side_set_by": None}
    game_state["Toxic_Spikes"] = {"p1_side_is_active": False, "p1_side_set_by": None, "p2_side_is_active": False, "p2_side_set_by": None}
    game_state["Nicknames"] = {}

def set_storm(game_state, p1, p2, game_actions, i):

    game_state["Sandstorm"]["Is_active"] = True

    if "p2a" in game_actions[i]:
        game_state["Sandstorm"]["Set_by"] = game_state["Nicknames"][game_actions[i].split("p2a: ")[1]]

    elif "p1a" in game_actions[i]:
        game_state["Sandstorm"]["Set_by"] = game_state["Nicknames"][game_actions[i].split("p1a: ")[1]]

def del_storm(game_state, p1, p2, game_actions, i):

    if(game_state["Sandstorm"]["Is_active"]):
        game_state["Sandstorm"]["Is_active"] = False
        game_state["Sandstorm"]["Set_by"] = None

def side_start(stats_dict,game_state, p1, p2, game_actions, i):

    if "Stealth Rock" in game_actions[i]:
        if "p2a" in game_actions[i]:
            game_state["Rocks"]["p1_side_is_active"] = True
            game_state["Rocks"]["p1_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]
            stats_dict[p2]["Pokemon"][game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]]["Rocks/Spikes_Set"] += 1

        elif "p1a" in game_actions[i]:
            game_state["Rocks"]["p2_side_is_active"] = True
            game_state["Rocks"]["p2_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]
            stats_dict[p1]["Pokemon"][game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]]["Rocks/Spikes_Set"] += 1

        else:
            if "p1" in game_actions[i]:
                game_state["Rocks"]["p1_side_is_active"] = True
                game_state["Rocks"]["p1_side_set_by"] = game_state["p2_active"]
                stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Rocks/Spikes_Set"] += 1

            else:
                game_state["Rocks"]["p2_side_is_active"] = True
                game_state["Rocks"]["p2_side_set_by"] = game_state["p1_active"]
                stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Rocks/Spikes_Set"] += 1

    elif "Toxic Spikes" in game_actions[i]:
        if "p1" in game_actions[i]:
            game_state["Toxic_Spikes"]["p1_side_is_active"] = True
            game_state["Toxic_Spikes"]["p1_side_set_by"] = game_state["p2_active"]
            stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Rocks/Spikes_Set"] += 1

        elif "p2" in game_actions[i]:
            game_state["Toxic_Spikes"]["p2_side_is_active"] = True
            game_state["Toxic_Spikes"]["p2_side_set_by"] = game_state["p1_active"]
            stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Rocks/Spikes_Set"] += 1

    elif "Spikes" in game_actions[i]:
        if "p1" in game_actions[i]:
            game_state["Spikes"]["p1_side_is_active"] = True
            game_state["Spikes"]["p1_side_set_by"] = game_state["p2_active"]
            stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Rocks/Spikes_Set"] += 1

        elif "p2" in game_actions[i]:
            game_state["Spikes"]["p2_side_is_active"] = True
            game_state["Spikes"]["p2_side_set_by"] = game_state["p1_active"]
            stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Rocks/Spikes_Set"] += 1

def start_status(stats_dict,game_state, p1, p2, game_actions, i):

    if("tox" in game_actions[i] or "psn" in game_actions[i]):
        poison_attribution(stats_dict,game_state, p1, p2, game_actions, i)

    if("brn" in game_actions[i]):
        burn_attribution(game_state, p1, p2, game_actions, i)

def poison_attribution(stats_dict,game_state, p1, p2, game_actions, i):

    if "Toxic Orb" in game_actions[i]:
        
        if "p1a" in game_actions[i]:
            game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": "Toxic Orb"}
        if "p2a" in game_actions[i]:
            game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": "Toxic Orb"}

    elif "[from]" not in game_actions[i] and "[of]" not in game_actions[i]:
        if "p1" in game_actions[i]:

            if("p2a" in game_actions[i-1]):
                stats_dict[p2]["Pokemon"][game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]]["Pkmn_Poisoned"] += 1
                game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]}
            
            elif game_state["Toxic_Spikes"]["p1_side_is_active"]:
                stats_dict[p2]["Pokemon"][game_state["Toxic_Spikes"]["p1_side_set_by"]]["Pkmn_Poisoned"] += 1
                game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["Toxic_Spikes"]["p1_side_set_by"]}
            
            else:
                stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Pkmn_Poisoned"] += 1
                game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["p2_active"]}
            
        
        if "p2" in game_actions[i]:

            if("p1a" in game_actions[i-1]):
                stats_dict[p1]["Pokemon"][game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]]["Pkmn_Poisoned"] += 1
                game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]}
            
            elif game_state["Toxic_Spikes"]["p2_side_is_active"]:
                stats_dict[p1]["Pokemon"][game_state["Toxic_Spikes"]["p2_side_set_by"]]["Pkmn_Poisoned"] += 1
                game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Toxic_Spikes"]["p2_side_set_by"]}
            
            else:
                stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Pkmn_Poisoned"] += 1
                game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["p1_active"]}
    else:
        if "|-status|p2a" in game_actions[i]:
            stats_dict[p1]["Pokemon"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1]]]["Pkmn_Poisoned"] += 1
            game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i].split("p1a: ")[1]]}

        if "|-status|p1a" in game_actions[i]:
            stats_dict[p2]["Pokemon"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1]]]["Pkmn_Poisoned"] += 1
            game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i].split("p2a: ")[1]]}

def burn_attribution(game_state, p1, p2, game_actions, i):

    if "Flame Orb" in game_actions[i]:
        
        if "p1a" in game_actions[i]:
            game_state["Burn"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": "Flame Orb"}
        if "p2a" in game_actions[i]:
            game_state["Burn"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": "Flame Orb"}

    elif "[from]" not in game_actions[i] and "[of]" not in game_actions[i]:
        if "p1" in game_actions[i]:

            if("p2a" in game_actions[i-1]):
                game_state["Burn"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]}
            else:
                game_state["Burn"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["p2_active"]}
            
        
        if "p2" in game_actions[i]:

            if("p1a" in game_actions[i-1]):
                game_state["Burn"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]}
            else:
                game_state["Burn"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["p1_active"]}
    else:
        if "|-status|p2a" in game_actions[i]:
            game_state["Burn"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i].split("p1a: ")[1]]}

        if "|-status|p1a" in game_actions[i]:
            game_state["Burn"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i].split("p2a: ")[1]]}


def end_status(game_state, p1, p2, game_actions, i):

    if("p1a" in game_actions[i]):

        if "tox" in game_actions[i] or "psn" in game_actions[i]:
            del game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]]
        elif "brn" in game_actions[i]:
            del game_state["Burn"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]]

    if("p2a" in game_actions[i]):

        if "tox" in game_actions[i] or "psn" in game_actions[i]:
            del game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]]
        elif "brn" in game_actions[i]:
            del game_state["Burn"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]]

    if("p1" in game_actions[i] and "p1a" not in game_actions[i]):

        if "tox" in game_actions[i] or "psn" in game_actions[i]:
            del game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1: ")[1].split("|")[0]]]
        elif "brn" in game_actions[i]:
            del game_state["Burn"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1: ")[1].split("|")[0]]]

    if("p2" in game_actions[i] and "p2a" not in game_actions[i]):

        if "tox" in game_actions[i] or "psn" in game_actions[i]:
            del game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2: ")[1].split("|")[0]]]
        elif "brn" in game_actions[i]:
            del game_state["Burn"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2: ")[1].split("|")[0]]]


def mega(stats_dict, game_state, p1, p2, p1_mons, p2_mons, game_actions, i):

    if("|detailschange|p2a" in game_actions[i]):

        p2_active = game_actions[i].split("|detailschange|p2a: ")[1].split("|")[1]

        if "," in p2_active:
            p2_active = p2_active.split(",")[0]

        p2_active_nick = game_actions[i].split("|detailschange|p2a: ")[1].split("|")[0]

        k = game_state[p2][game_state["p2_active"]]["Kills"]
        d = game_state[p2][game_state["p2_active"]]["Deaths"]
        hp = game_state[p2][game_state["p2_active"]]["HP"]
        

        p2_mons.remove(game_state["p2_active"])
        p2_mons.append(p2_active)

        tox = False
        for instance in game_state["Toxic"]["On_p2"]:
            if instance == game_state["p2_active"]:
                tox = True

        if tox:
            game_state["Toxic"]["On_p2"][p2_active] = game_state["Toxic"]["On_p2"][game_state["p2_active"]]
            game_state["Toxic"]["On_p2"][game_state["p2_active"]]

        brn = False
        for instance in game_state["Burn"]["On_p2"]:
            if instance == game_state["p2_active"]:
                brn = True

        if brn:
            game_state["Burn"]["On_p2"][p2_active] = game_state["Burn"]["On_p2"][game_state["p2_active"]]
            game_state["Burn"]["On_p2"][game_state["p2_active"]]

        new_stat_dict = {}
        for stat in stats_dict[p2]["Pokemon"][game_state["p2_active"]]:
            new_stat_dict[stat] = stats_dict[p2]["Pokemon"][game_state["p2_active"]][stat]

        del game_state[p2][game_state["p2_active"]]
        del stats_dict[p2]["Pokemon"][game_state["p2_active"]]

        stats_dict[p2]["Pokemon"][p2_active] = new_stat_dict

        game_state["p2_active"] = p2_active
        game_state["p2_active_nick"] = p2_active_nick
        game_state["Nicknames"][p2_active_nick] = p2_active

        game_state[p2][game_state["p2_active"]] = {"Kills":k,"Deaths":d,"HP":hp}

        

    if("|detailschange|p1a" in game_actions[i]):

        p1_active = game_actions[i].split("|detailschange|p1a: ")[1].split("|")[1]

        if "," in p1_active:
            p1_active = p1_active.split(",")[0]

        p1_active_nick = game_actions[i].split("|detailschange|p1a: ")[1].split("|")[0]

        k = game_state[p1][game_state["p1_active"]]["Kills"]
        d = game_state[p1][game_state["p1_active"]]["Deaths"]
        hp = game_state[p1][game_state["p1_active"]]["HP"]

        p1_mons.remove(game_state["p1_active"])
        p1_mons.append(p1_active)

    
        tox = False
        for instance in game_state["Toxic"]["On_p1"]:
            if instance == game_state["p1_active"]:
                tox = True
        if tox:
            game_state["Toxic"]["On_p1"][p1_active] = game_state["Toxic"]["On_p1"][game_state["p1_active"]]
            game_state["Toxic"]["On_p1"][game_state["p1_active"]]

        brn = False
        for instance in game_state["Burn"]["On_p1"]:
            if instance == game_state["p1_active"]:
                brn = True

        if brn:
            game_state["Burn"]["On_p1"][p1_active] = game_state["Burn"]["On_p1"][game_state["p1_active"]]
            del game_state["Burn"]["On_p1"][game_state["p1_active"]]

        new_stat_dict = {}
        for stat in stats_dict[p1]["Pokemon"][game_state["p1_active"]]:
            new_stat_dict[stat] = stats_dict[p1]["Pokemon"][game_state["p1_active"]][stat]

        del game_state[p1][game_state["p1_active"]]
        del stats_dict[p1]["Pokemon"][game_state["p1_active"]]

        stats_dict[p1]["Pokemon"][p1_active] = new_stat_dict

        game_state["p1_active"] = p1_active
        game_state["p1_active_nick"] = p1_active_nick
        game_state["Nicknames"][p1_active_nick] = p1_active

        game_state[p1][game_state["p1_active"]] = {"Kills":k,"Deaths":d,"HP":hp}

def handle_forfeit(game_state, p1, p2, p1_mons, p2_mons, game_actions, i):

    forefeit_name = game_actions[i].split("|-message|")[1].split(" forfeited.")[0]
    remaining_mons = 0
    for pokemon in game_state[forefeit_name]:

        if game_state[forefeit_name][pokemon]["Deaths"] == 0:
            game_state[forefeit_name][pokemon]["Deaths"] = 1
            remaining_mons += 1

    if p1 == forefeit_name:
        game_state[p1][game_state["p1_active"]]["Kills"] += remaining_mons
    else:
        game_state[p2][game_state["p2_active"]]["Kills"] += remaining_mons

def check_illusion(game_state, p1, p2, p1_mons, p2_mons, log):
    p1_illusion = False
    p2_illusion = False
    learnsets = None

    if "Zoroark" in p1_mons or "Zoroark-Hisui" in p1_mons or "Zorua" in p1_mons or \
        "Zorua-Hisui" in p1_mons:

        p1_illusion = True

        with open("Pokemon_Info/learnsets.json") as moves:
            learnsets = json.load(moves)

    elif "Zoroark" in p2_mons or "Zoroark-Hisui" in p2_mons or "Zorua" in p2_mons or \
        "Zorua-Hisui" in p2_mons:

        p2_illusion = True

        with open("Pokemon_Info/learnsets.json") as moves:
            learnsets = json.load(moves)

    return p1_illusion, p2_illusion,learnsets

def remove_non_alpha(input_str):
    output_str = (''.join([i for i in input_str if i.isalnum()])).lower()
    return output_str

def check_movepool_p1(game_state, p1, p2, game_actions, i, learnsets):

    mon = remove_non_alpha(game_state["p1_active"])

    if mon[-4:] == "mega":
        mon=mon[:-4]

    if mon not in RESTRICT_MOVE_CHECKING:
        move = remove_non_alpha(game_actions[i].split("|")[3])
        #print(mon, "||", move, "||", move in learnsets[mon])

        if mon in learnsets:
            if move in learnsets[mon]:
                return True
            else:
                return False
    
def check_movepool_p2(game_state, p1, p2, game_actions, i, learnsets):

    mon = remove_non_alpha(game_state["p2_active"])

    if mon[-4:] == "mega":
        mon=mon[:-4]

    if mon not in RESTRICT_MOVE_CHECKING:
        move = remove_non_alpha(game_actions[i].split("|")[3])
        #print(mon, "||", move, "||", move in learnsets[mon])

        if mon in learnsets:
            if move in learnsets[mon]:
                return True
            else:
                return False
        
def set_stats_dict(game_state, p1, p2, p1_mons, p2_mons, log):
    stats_dict = {p1:{"Win":0, "Pokemon":{}},p2:{"Win":0, "Pokemon":{}}}

    for pokemon in p1_mons:
        stats_dict[p1]["Pokemon"][pokemon] = {"Dmg_Dealt":0,"Dmg_Taken":0,"Switched_out":0,"Pkmn_Poisoned":0,"Crits":0,"Rocks/Spikes_Set":0,"Moves_Used":{}}

    for pokemon in p2_mons:
        stats_dict[p2]["Pokemon"][pokemon] = {"Dmg_Dealt":0,"Dmg_Taken":0,"Switched_out":0,"Pkmn_Poisoned":0,"Crits":0,"Rocks/Spikes_Set":0,"Moves_Used":{}}

    return stats_dict

def add_move_p1(stats_dict,game_state, p1, p2, game_actions, i):
    mon = game_state["p1_active"]
    move = game_actions[i].split("|")[3]

    if (stats_dict[p1]["Pokemon"][mon]["Moves_Used"].get(move)):
        stats_dict[p1]["Pokemon"][mon]["Moves_Used"][move] += 1
    else:
        stats_dict[p1]["Pokemon"][mon]["Moves_Used"][move] = 1

def add_move_p2(stats_dict,game_state, p1, p2, game_actions, i):
    mon = game_state["p2_active"]
    move = game_actions[i].split("|")[3]

    if (stats_dict[p2]["Pokemon"][mon]["Moves_Used"].get(move)):
        stats_dict[p2]["Pokemon"][mon]["Moves_Used"][move] += 1
    else:
        stats_dict[p2]["Pokemon"][mon]["Moves_Used"][move] = 1

def track_damage(stats_dict,game_state, p1, p2, game_actions, i):
    acceptable_pre_move_states = ["-hint","|-enditem","|-sideend","-activate","|-crit","-damage|p1a","-damage|p2a", "move|p2a","Focus Sash", "move|p1a", "-supereffective", "|-anim","-resisted"]
    if "-damage|p1a" in game_actions[i] and any(state in game_actions[i-1] for state in acceptable_pre_move_states):
        
        hp = game_actions[i].split("/100")[0][-3:]
        if hp[0] == "|":
            hp = hp[1:]
        if hp[1] == "|":
            hp = hp[2:]
        if "0 fnt" in game_actions[i]:
                hp = 0
        hp = int(hp)

        damage_taken = game_state[p1][game_state["p1_active"]]["HP"] - hp
        game_state[p1][game_state["p1_active"]]["HP"] = hp

        stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Dmg_Taken"] += damage_taken
        stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Dmg_Dealt"] += damage_taken

        #print(game_state["p2_active"], "Dealt", damage_taken, "to", game_state["p1_active"])

    elif "-damage|p2a" in game_actions[i] and any(state in game_actions[i-1] for state in acceptable_pre_move_states):
        
        hp = game_actions[i].split("/100")[0][-3:]
        if hp[0] == "|":
            hp = hp[1:]
        if hp[1] == "|":
            hp = hp[2:]
        if "0 fnt" in game_actions[i]:
                hp = 0
        hp = int(hp)

        damage_taken = game_state[p2][game_state["p2_active"]]["HP"] - hp
        game_state[p2][game_state["p2_active"]]["HP"] = hp

        stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Dmg_Taken"] += damage_taken
        stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Dmg_Dealt"] += damage_taken

        #print(game_state["p1_active"], "Dealt", damage_taken, "to", game_state["p2_active"])

    else:

        if "-damage|p2a" in game_actions[i]:
            #print(game_actions[i])
            hp = game_actions[i].split("/100")[0][-3:]
            if hp[0] == "|":
                hp = hp[1:]
            if hp[1] == "|":
                hp = hp[2:]
            if "fnt" in game_actions[i] and "[from]" in game_actions[i]:
                hp = 0
            hp = int(hp)

            game_state[p2][game_state["p2_active"]]["HP"] = hp

        elif "-damage|p1a" in game_actions[i]:
            #print(game_actions[i])
            hp = game_actions[i].split("/100")[0][-3:]
            if hp[0] == "|":
                hp = hp[1:]
            if hp[1] == "|":
                hp = hp[2:]

            if "fnt" in game_actions[i] and "[from]" in game_actions[i]:
                hp = 0
            hp = int(hp)

            game_state[p1][game_state["p1_active"]]["HP"] = hp

def track_heal(stats_dict,game_state, p1, p2, game_actions, i):
    if "|-heal|p1a" in game_actions[i]:
        hp = game_actions[i].split("/100")[0][-3:]
        if hp[0] == "|":
            hp = hp[1:]
        if hp[1] == "|":
            hp = hp[2:]

        game_state[p1][game_state["p1_active"]]["HP"] = int(hp)

    elif "|-heal|p2a" in game_actions[i]:
        hp = game_actions[i].split("/100")[0][-3:]
        if hp[0] == "|":
            hp = hp[1:]
        if hp[1] == "|":
            hp = hp[2:]

        game_state[p2][game_state["p2_active"]]["HP"] = int(hp)

def track_crit(stats_dict,game_state, p1, p2, game_actions, i):
    if "|-crit|p1a" in game_actions[i]:
        stats_dict[p2]["Pokemon"][game_state["p2_active"]]["Crits"] += 1

    elif "|-crit|p2a" in game_actions[i]:
        stats_dict[p1]["Pokemon"][game_state["p1_active"]]["Crits"] += 1

def get_stats(game_state, p1, p2, p1_mons, p2_mons, log):

    stats_dict = set_stats_dict(game_state, p1, p2, p1_mons, p2_mons, log)

    #check for zoroark and if it's there take measures to avoid errors
    p1_illusion, p2_illusion, learnsets = check_illusion(game_state, p1, p2, p1_mons, p2_mons, log)
    
    
    turn_num = 1
    for turn in log:
        #print("Beginning of Turn", turn_num)
        #print(p1, "Active Mon", game_state["p1_active"])
        #print(p2, "Active Mon", game_state["p2_active"])

        game_actions = turn.split("\n")
        #print("Turn:", turn_num)

        for i in range(0, len(game_actions)):

            if "forfeited" in game_actions[i]:
                handle_forfeit(game_state, p1, p2, p1_mons, p2_mons, game_actions, i)

            if "|switch|" in game_actions[i] or "|drag|p" in game_actions[i]:
                #print(game_actions[i])
                switch(stats_dict,game_state, p1, p2, p1_mons, p2_mons, game_actions, i,turn_num)

            if "|faint|" in game_actions[i]:
                #print(game_actions[i])
                kd_attribution(game_state, p1, p2, game_actions, i)

            if "|replace|" in game_actions[i]:
                #this is for zoruark and stuff
                #print(game_actions[i])
                replace_pokemon(game_state, p1, p2, game_actions, i)

            if "|detailschange|" in game_actions[i]:
                #print(game_actions[i])
                mega(stats_dict, game_state, p1, p2, p1_mons, p2_mons, game_actions, i)

            if "|-weather|Sandstorm|[from]" in game_actions[i]:
                #print(game_actions[i])
                set_storm(game_state, p1, p2, game_actions, i)

            if "|-weather|none" in game_actions[i]:
                del_storm(game_state, p1, p2, game_actions, i)

            if "|-weather|Sandstorm|[from]" in game_actions[i]:
                #print(game_actions[i])
                set_storm(game_state, p1, p2, game_actions, i)

            if "|-sidestart" in game_actions[i]:
                #print(game_actions[i])
                side_start(stats_dict,game_state, p1, p2, game_actions, i)

            if "|-status|" in game_actions[i]:
                #print(game_actions[i])
                start_status(stats_dict,game_state, p1, p2, game_actions, i)

            if "|-curestatus|" in game_actions[i]:
                end_status(game_state, p1, p2, game_actions, i)

            if "|move|p1a:" in game_actions[i]:
                add_move_p1(stats_dict,game_state, p1, p2, game_actions, i)

            if "|move|p2a:" in game_actions[i]:
                add_move_p2(stats_dict,game_state, p1, p2, game_actions, i)

            if "|-damage|" in game_actions[i]:
                track_damage(stats_dict,game_state, p1, p2, game_actions, i)
            
            if "|-heal|" in game_actions[i]:
                track_heal(stats_dict,game_state, p1, p2, game_actions, i)

            if "|-crit" in game_actions[i]:
                print
                track_crit(stats_dict,game_state, p1, p2, game_actions, i)

            #check movepools of pokemon every turn to see if a zoroark is out
            if p1_illusion:
                
                if "|move|p1a:" in game_actions[i]:
                    check_movepool_p1(game_state, p1, p2, game_actions, i,learnsets)

            if p2_illusion:
                
                if "|move|p2a:" in game_actions[i]:
                    check_movepool_p2(game_state, p1, p2, game_actions, i,learnsets)

        #print(p1, "Active Mon", game_state["p1_active"])
        #print(p2, "Active Mon", game_state["p2_active"])
        #print("End of Turn", turn_num)


        turn_num+=1

    return stats_dict

def get_match_result(message):
    """
    Get just K/D info here
    """
    
    replay = ""
    for word in message.replace("\n"," ").split(" "):
        if "replay.pokemonshowdown.com" in word:
            replay = word

    log = get_battle_log(replay)
    game_state, p1, p2, p1_mons, p2_mons = get_teams(log)
    set_state(game_state)
    get_leads(log, game_state)
    get_KD_stats(game_state, p1, p2, p1_mons, p2_mons, log)

    return get_string_output(game_state, p1, p2, p1_mons, p2_mons, log)


def get_KD_stats(game_state, p1, p2, p1_mons, p2_mons, log):
    stats_dict = set_stats_dict(game_state, p1, p2, p1_mons, p2_mons, log)

    #check for zoroark and if it's there take measures to avoid errors
    p1_illusion, p2_illusion, learnsets = check_illusion(game_state, p1, p2, p1_mons, p2_mons, log)
    
    
    turn_num = 1
    for turn in log:
        #print("Beginning of Turn", turn_num)
        #print(p1, "Active Mon", game_state["p1_active"])
        #print(p2, "Active Mon", game_state["p2_active"])

        game_actions = turn.split("\n")
        #print("Turn:", turn_num)

        for i in range(0, len(game_actions)):

            if "forfeited" in game_actions[i]:
                handle_forfeit(game_state, p1, p2, p1_mons, p2_mons, game_actions, i)

            if "|switch|" in game_actions[i] or "|drag|p" in game_actions[i]:
                #print(game_actions[i])
                switch(stats_dict,game_state, p1, p2, p1_mons, p2_mons, game_actions, i,turn_num)

            if "|faint|" in game_actions[i]:
                #print(game_actions[i])
                kd_attribution(game_state, p1, p2, game_actions, i)

            if "|replace|" in game_actions[i]:
                #this is for zoruark and stuff
                #print(game_actions[i])
                replace_pokemon(game_state, p1, p2, game_actions, i)

            if "|detailschange|" in game_actions[i]:
                #print(game_actions[i])
                mega(stats_dict, game_state, p1, p2, p1_mons, p2_mons, game_actions, i)

            if "|-weather|Sandstorm|[from]" in game_actions[i]:
                #print(game_actions[i])
                set_storm(game_state, p1, p2, game_actions, i)

            if "|-weather|none" in game_actions[i]:
                del_storm(game_state, p1, p2, game_actions, i)

            if "|-weather|Sandstorm|[from]" in game_actions[i]:
                #print(game_actions[i])
                set_storm(game_state, p1, p2, game_actions, i)

            if "|-sidestart" in game_actions[i]:
                #print(game_actions[i])
                side_start(stats_dict,game_state, p1, p2, game_actions, i)

            if "|-status|" in game_actions[i]:
                #print(game_actions[i])
                start_status(stats_dict,game_state, p1, p2, game_actions, i)

            if "|-curestatus|" in game_actions[i]:
                end_status(game_state, p1, p2, game_actions, i)

            #check movepools of pokemon every turn to see if a zoroark is out
            if p1_illusion:
                
                if "|move|p1a:" in game_actions[i]:
                    check_movepool_p1(game_state, p1, p2, game_actions, i,learnsets)

            if p2_illusion:
                
                if "|move|p2a:" in game_actions[i]:
                    check_movepool_p2(game_state, p1, p2, game_actions, i,learnsets)

        #print(p1, "Active Mon", game_state["p1_active"])
        #print(p2, "Active Mon", game_state["p2_active"])
        #print("End of Turn", turn_num)


        turn_num+=1

    return stats_dict


def get_match_stats(message):

    """
    Get all of the info like damage and everything
    """

    replay = ""
    for word in message.split(" "):
        if "replay.pokemonshowdown.com" in word:
            replay = word

    log = get_battle_log(replay)
    game_state, p1, p2, p1_mons, p2_mons = get_teams(log)
    set_state(game_state)
    get_leads(log, game_state)
    stats_dict = get_stats(game_state, p1, p2, p1_mons, p2_mons, log)

    for pokemon in game_state[p1]:
        if pokemon != game_state["p1_active"]:
            stats_dict[p1]["Pokemon"][pokemon]["Switched_out"] -= game_state[p1][pokemon]["Deaths"]

    for pokemon in game_state[p2]:
        if pokemon != game_state["p2_active"]:
            stats_dict[p2]["Pokemon"][pokemon]["Switched_out"] -= game_state[p2][pokemon]["Deaths"]

    for coach in [p1,p2]:
        for mon in game_state[coach]:
            stats_dict[coach]["Pokemon"][mon]["Kills"] = game_state[coach][mon]["Kills"]
            stats_dict[coach]["Pokemon"][mon]["Deaths"] = game_state[coach][mon]["Deaths"]

    p1_survivors = len(p1_mons)
    for pokemon in game_state[p1]:
        if game_state[p1][pokemon]["Deaths"] >= 1:
            p1_survivors -= 1

    p2_survivors = len(p2_mons)
    for pokemon in game_state[p2]:
        if game_state[p2][pokemon]["Deaths"] >= 1:
            p2_survivors -= 1

    if p1_survivors > p2_survivors:
        stats_dict[p1]["Wins"] = 1
        stats_dict[p1]["Losses"] = 0
        stats_dict[p1]["Diff"] = p1_survivors
        stats_dict[p2]["Wins"] = 0
        stats_dict[p2]["Losses"] = 1
        stats_dict[p2]["Diff"] = (-1) * p1_survivors

        for mon in p1_mons:
            stats_dict[p1]["Pokemon"][mon]["Wins"] = 1
            stats_dict[p1]["Pokemon"][mon]["Losses"] = 0
            stats_dict[p1]["Pokemon"][mon]["Diff"] = p1_survivors

        for mon in p2_mons:
            stats_dict[p2]["Pokemon"][mon]["Wins"] = 0
            stats_dict[p2]["Pokemon"][mon]["Losses"] = 1
            stats_dict[p2]["Pokemon"][mon]["Diff"] = (-1) * p1_survivors

    elif p1_survivors < p2_survivors:
        stats_dict[p1]["Win"] = 0
        stats_dict[p1]["Losses"] = 1
        stats_dict[p1]["Diff"] = (-1) * p2_survivors
        stats_dict[p2]["Win"] = 1
        stats_dict[p2]["Losses"] = 0
        stats_dict[p2]["Diff"] = p2_survivors

        for mon in p1_mons:
            stats_dict[p1]["Pokemon"][mon]["Wins"] = 0
            stats_dict[p1]["Pokemon"][mon]["Losses"] = 1
            stats_dict[p1]["Pokemon"][mon]["Diff"] = (-1) * p2_survivors

        for mon in p2_mons:
            stats_dict[p2]["Pokemon"][mon]["Wins"] = 1
            stats_dict[p2]["Pokemon"][mon]["Losses"] = 0
            stats_dict[p2]["Pokemon"][mon]["Diff"] = p2_survivors

    return game_state, stats_dict, log


if __name__ == "__main__":
    print(get_match_result("https://replay.pokemonshowdown.com/gen9natdexdraft-2217122826"))
