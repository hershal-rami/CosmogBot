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

    battle_log = (("\n").join(json_ver["log"])).split("|turn")
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
        game_state[p1][mon] = {"Kills":0, "Deaths":0}

    for mon in p2_mons:
        game_state[p2][mon] = {"Kills":0, "Deaths":0}

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



def switch(game_state, p1, p2, p1_mons, p2_mons, game_actions, i):
    
    if("|switch|p2a" in game_actions[i]):

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
                game_state[p2][p2_active] = {"Deaths": game_state[p2][remove_mon]["Deaths"], "Kills" : game_state[p2][remove_mon]["Kills"]}
                game_state[p2].pop(remove_mon)
                p2_mons.remove(remove_mon)
                p2_mons.append(p2_active)

    if("|switch|p1a" in game_actions[i]):

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
                game_state[p1][p1_active] = {"Deaths": game_state[p1][remove_mon]["Deaths"], "Kills" : game_state[p1][remove_mon]["Kills"]}
                game_state[p1].pop(remove_mon)
                p1_mons.remove(remove_mon)
                p1_mons.append(p1_active)



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

            if game_state[p2][game_state["Toxic"]["On_p1"][game_state["p1_active"]]["Set_by"]] == "Toxic Orb":
                game_state[p2][game_state["p2_active"]]["Kills"] += 1
            else:
                game_state[p2][game_state["Toxic"]["On_p1"][game_state["p1_active"]]["Set_by"]]["Kills"] += 1

        elif "-damage|p2a" in game_actions[i-1]:
            game_state[p2][game_state["p2_active"]]["Deaths"] = 1

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
        if game_state[p1][pokemon]["Deaths"] == 1:
            p1_survivors -= 1

    p2_survivors = len(p2_mons)
    for pokemon in game_state[p2]:
        if game_state[p2][pokemon]["Deaths"] == 1:
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

def side_start(game_state, p1, p2, game_actions, i):

    if "Stealth Rock" in game_actions[i]:
        if "p2a" in game_actions[i]:
            game_state["Rocks"]["p1_side_is_active"] = True
            game_state["Rocks"]["p1_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]

        elif "p1a" in game_actions[i]:
            game_state["Rocks"]["p2_side_is_active"] = True
            game_state["Rocks"]["p2_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]

        else:
            if "p1" in game_actions[i]:
                game_state["Rocks"]["p1_side_is_active"] = True
                game_state["Rocks"]["p1_side_set_by"] = game_state["p2_active"]
            else:
                game_state["Rocks"]["p2_side_is_active"] = True
                game_state["Rocks"]["p2_side_set_by"] = game_state["p1_active"]

    elif "Toxic Spikes" in game_actions[i]:
        if "p1" in game_actions[i]:
            game_state["Toxic_Spikes"]["p1_side_is_active"] = True
            game_state["Toxic_Spikes"]["p1_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]

        elif "p2" in game_actions[i]:
            game_state["Toxic_Spikes"]["p2_side_is_active"] = True
            game_state["Toxic_Spikes"]["p2_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]

    elif "Spikes" in game_actions[i]:
        if "p1" in game_actions[i]:
            game_state["Spikes"]["p1_side_is_active"] = True
            game_state["Spikes"]["p1_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]

        elif "p2" in game_actions[i]:
            game_state["Spikes"]["p2_side_is_active"] = True
            game_state["Spikes"]["p2_side_set_by"] = game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]


def start_status(game_state, p1, p2, game_actions, i):

    if("tox" in game_actions[i] or "psn" in game_actions[i]):
        poison_attribution(game_state, p1, p2, game_actions, i)

    if("brn" in game_actions[i]):
        burn_attribution(game_state, p1, p2, game_actions, i)

def poison_attribution(game_state, p1, p2, game_actions, i):

    if "Toxic Orb" in game_actions[i]:
        
        if "p1a" in game_actions[i]:
            game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": "Toxic Orb"}
        if "p2a" in game_actions[i]:
            game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": "Toxic Orb"}

    elif "[from]" not in game_actions[i] and "[of]" not in game_actions[i]:
        if "p1" in game_actions[i]:

            if("p2a" in game_actions[i-1]):
                game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i-1].split("p2a: ")[1].split("|")[0]]}
            elif game_state["Toxic_Spikes"]["p1_side_is_active"]:
                game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["Toxic_Spikes"]["p1_side_set_by"]}
            else:
                game_state["Toxic"]["On_p1"][game_state["Nicknames"][game_actions[i].split("p1a: ")[1].split("|")[0]]] = {"Set_by": game_state["p2_active"]}
            
        
        if "p2" in game_actions[i]:

            if("p1a" in game_actions[i-1]):
                game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i-1].split("p1a: ")[1].split("|")[0]]}
            elif game_state["Toxic_Spikes"]["p2_side_is_active"]:
                game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Toxic_Spikes"]["p2_side_set_by"]}
            else:
                game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["p1_active"]}
    else:
        if "|-status|p2a" in game_actions[i]:
            game_state["Toxic"]["On_p2"][game_state["Nicknames"][game_actions[i].split("p2a: ")[1].split("|")[0]]] = {"Set_by": game_state["Nicknames"][game_actions[i].split("p1a: ")[1]]}

        if "|-status|p1a" in game_actions[i]:
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


def mega(game_state, p1, p2, p1_mons, p2_mons, game_actions, i):

    if("|detailschange|p2a" in game_actions[i]):

        p2_active = game_actions[i].split("|detailschange|p2a: ")[1].split("|")[1]

        if "," in p2_active:
            p2_active = p2_active.split(",")[0]

        p2_active_nick = game_actions[i].split("|detailschange|p2a: ")[1].split("|")[0]

        k = game_state[p2][game_state["p2_active"]]["Kills"]
        d = game_state[p2][game_state["p2_active"]]["Deaths"]
        del game_state[p2][game_state["p2_active"]]

        p2_mons.remove(game_state["p2_active"])
        p2_mons.append(p2_active)

        game_state["p2_active"] = p2_active
        game_state["p2_active_nick"] = p2_active_nick
        game_state["Nicknames"][p2_active_nick] = p2_active

        game_state[p2][game_state["p2_active"]] = {"Kills":k,"Deaths":d}

        

    if("|detailschange|p1a" in game_actions[i]):

        p1_active = game_actions[i].split("|detailschange|p1a: ")[1].split("|")[1]

        if "," in p1_active:
            p1_active = p1_active.split(",")[0]

        p1_active_nick = game_actions[i].split("|detailschange|p1a: ")[1].split("|")[0]

        k = game_state[p1][game_state["p1_active"]]["Kills"]
        d = game_state[p1][game_state["p1_active"]]["Deaths"]
        del game_state[p1][game_state["p1_active"]]

        p1_mons.remove(game_state["p1_active"])
        p1_mons.append(p1_active)

        game_state["p1_active"] = p1_active
        game_state["p1_active_nick"] = p1_active_nick
        game_state["Nicknames"][p1_active_nick] = p1_active

        game_state[p1][game_state["p1_active"]] = {"Kills":k,"Deaths":d}

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
        game_state[p1][game_state["p1_active"]]["Kills"] += remaining_mons

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

    mon = remove_non_alpha(game_actions[i].split("|move|p1a: ")[1].split("|")[0])

    if mon not in RESTRICT_MOVE_CHECKING:
        move = remove_non_alpha(game_actions[i].split("|")[3])
        #print(mon, "||", move, "||", move in learnsets[mon])

        if move in learnsets[mon]:
            return True
        else:
            return False
    
def check_movepool_p2(game_state, p1, p2, game_actions, i, learnsets):

    mon = remove_non_alpha(game_actions[i].split("|move|p2a: ")[1].split("|")[0])

    if mon not in RESTRICT_MOVE_CHECKING:
        move = remove_non_alpha(game_actions[i].split("|")[3])
        #print(mon, "||", move, "||", move in learnsets[mon])

        if move in learnsets[mon]:
            return True
        else:
            return False
        
def get_stats(game_state, p1, p2, p1_mons, p2_mons, log):

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

            if "|switch|" in game_actions[i]:
                #print(game_actions[i])
                switch(game_state, p1, p2, p1_mons, p2_mons, game_actions, i)

            if "|faint|" in game_actions[i]:
                #print(game_actions[i])
                kd_attribution(game_state, p1, p2, game_actions, i)

            if "|replace|" in game_actions[i]:
                #this is for zoruark and stuff
                #print(game_actions[i])
                replace_pokemon(game_state, p1, p2, game_actions, i)

            if "|detailschange|" in game_actions[i]:
                #print(game_actions[i])
                mega(game_state, p1, p2, p1_mons, p2_mons, game_actions, i)

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
                side_start(game_state, p1, p2, game_actions, i)

            if "|-status|" in game_actions[i]:
                #print(game_actions[i])
                start_status(game_state, p1, p2, game_actions, i)

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

def get_match_result(message):
    
    replay = ""
    for word in message.split(" "):
        if "replay.pokemonshowdown.com" in word:
            replay = word

    log = get_battle_log(replay)
    game_state, p1, p2, p1_mons, p2_mons = get_teams(log)
    set_state(game_state)
    get_leads(log, game_state)
    get_stats(game_state, p1, p2, p1_mons, p2_mons, log)

    return get_string_output(game_state, p1, p2, p1_mons, p2_mons, log)
