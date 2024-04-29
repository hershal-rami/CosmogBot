from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import os
from replay_analyze import get_match_stats

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/MBTL_STATS_DB'

from sqlalchemy import event
from sqlalchemy import text
db = SQLAlchemy(app)


def setup():

    if os.path.exists("replays_in_db.json"):
        #do not run this function more than once!
        return
    else:
        with app.app_context():
            connection = db.session.connection()
            with open("replays_in_db.json","w") as f:
                json.dump({"Regular_Season":[],"Playoffs":[],"Championships":[]},f,indent=4)
            with open("error_replays_db.json","w") as f:
                json.dump({"Regular_Season":[],"Playoffs":[],"Championships":[]},f,indent=4)

            
            connection.execute( text("INSERT into Div_Stats values(0,0,\'Ultra\')") )
            connection.execute( text("INSERT into Div_Stats values(1,0,\'Dusk\')") )
            connection.execute( text("INSERT into Div_Stats values(2,0,\'Dawn\')") )
            connection.execute( text("INSERT into Div_Stats values(3,0,\'Prism\')") )
            connection.execute( text("INSERT into Div_Stats values(99,0,\'Other\')") )
            connection.commit()


            #setup pokemon data from showdown pokedex
            with open("Pokemon_Info/pokedex.ts", "r") as dex_f:
                dex = dex_f.read()
                dex = dex.split("SpeciesData} = {\n")[1]
                dex = dex.split(": {\n")

                form_num = 0
                prev_num = 0
                for i in range(1,len(dex) -1 ):
                    name = dex[i].split("name: \"")[1].split("\",")[0]

                    num = int(dex[i].split("num: ")[1].split(",")[0]) + 100000

                    types = []
                    type_str = dex[i].split("types: [\"")[1].split("],")[0]
                    for pkmn_type in type_str.split(","):
                        types.append(pkmn_type.strip().strip("\""))


                    if num == form_num:
                        num = prev_num + 10000
                    else:
                        form_num = num
                    prev_num = num
                    
                    hp = int(dex[i].split("hp: ")[1].split(",")[0])
                    atk = int(dex[i].split("atk: ")[1].split(",")[0])
                    defense = int(dex[i].split("def: ")[1].split(",")[0])
                    spa = int(dex[i].split("spa: ")[1].split(",")[0])
                    spd = int(dex[i].split("spd: ")[1].split(",")[0])
                    spe = int(dex[i].split("spe: ")[1].split("}")[0])
                    
                    if len(types)==1:
                        connection.execute(text(
                            f"INSERT into PKMN_Stats values({num},\'{types[0]}\', NULL,{hp},{atk},{defense},{spa},{spd},{spe},\"{name}\")") )
                        
                    else:
                        connection.execute(text(
                            f"INSERT into PKMN_Stats values({num},\'{types[0]}\', \'{types[1]}\',{hp},{atk},{defense},{spa},{spd},{spe},\"{name}\")") )
                connection.commit()
                
        

def db_insert_game(stats_dict, div,season, post_season=False,championship=False):
    with app.app_context():
        connection = db.session.connection()

        p_id_list= []
        for player in stats_dict:
            p = stats_dict[player]
            result = connection.execute( text(f"SELECT p_id from Player_Stats where p_name = \"{player}\"") )
            num_results = result.rowcount
            

            if num_results == 0:
                result = connection.execute( text("SELECT p_id from Player_Stats") )
                p_id = result.rowcount
                p_id_list.append((p_id,player))
                if not post_season:
                    connection.execute(text(
                            f"INSERT into Player_Stats values({p_id},\'{player}\', {p["Win"]},{p["Losses"]},0,0,0,{p["Diff"]})") )
                elif post_season and not championship:
                    connection.execute(text(
                            f"INSERT into Player_Stats values({p_id},\'{player}\', {p["Win"]},{p["Losses"]},{p["Win"]},{p["Losses"]},0,{p["Diff"]})") )
                elif post_season and championship:
                    connection.execute(text(
                            f"INSERT into Player_Stats values({p_id},\'{player}\', {p["Win"]},{p["Losses"]},{p["Win"]},{p["Losses"]},{p["Win"]},{p["Diff"]})") )
                    
            else:
                p_id_list.append((result.first()[0],player))
                if not post_season:
                    connection.execute(text(
                    f"""UPDATE Player_Stats SET p_wins=p_wins+{p["Win"]}, p_losses=p_losses+{p["Losses"]}, p_diff = p_diff+{p["Diff"]} WHERE p_name =\"{player}\"
                    """
                ))
                    
                elif post_season and not championship:
                    connection.execute(text(
                    f"""UPDATE Player_Stats SET p_wins=p_wins+{p["Win"]}, p_losses=p_losses+{p["Losses"]}, p_post_season_w=p_post_season_w+{p["Win"]}, p_post_season_l=p_post_season_l+{p["Losses"]}, p_diff=p_diff+{p["Diff"]} WHERE p_name =\"{player}\"
                    """
                ))
                elif post_season and championship:
                    connection.execute(text(
                    f"""UPDATE Player_Stats SET p_wins=p_wins+{p["Win"]}, p_losses=p_losses+{p["Losses"]}, p_post_season_w=p_post_season_w+{p["Win"]}, p_post_season_l=p_post_season_l+{p["Losses"]}, p_championships=p_championships+{p["Win"]},p_diff=p_diff+{p["Diff"]} WHERE p_name =\"{player}\"
                    """
                ))

        result = connection.execute( text(f"SELECT * from Matchup_Stats where p_id_1 = \"{p_id_list[0][0]}\" and p_id_2 = \"{p_id_list[1][0]}\"") )
        num_results_1 = result.rowcount
        result = connection.execute( text(f"SELECT * from Matchup_Stats where p_id_1 = \"{p_id_list[1][0]}\" and p_id_2 = \"{p_id_list[0][0]}\"") )
        num_results_2 = result.rowcount

        if num_results_1 == 0 and num_results_2 == 0:
            connection.execute(text(
                    f"INSERT into Matchup_Stats values({p_id_list[0][0]},{p_id_list[1][0]}, {stats_dict[p_id_list[0][1]]["Win"]},{stats_dict[p_id_list[1][1]]["Win"]},{stats_dict[p_id_list[0][1]]["Diff"]})") )
        elif num_results_1 >= 1 and num_results_2 == 0:
            connection.execute(text(
            f"""UPDATE Matchup_Stats SET p1_wins=p1_wins+{stats_dict[p_id_list[0][1]]["Win"]}, p2_wins=p2_wins+{stats_dict[p_id_list[1][1]]["Win"]},p1_diff=p1_diff+{stats_dict[p_id_list[0][1]]["Diff"]} WHERE p_id_1 =\"{p_id_list[0][0]}\" and p_id_2 =\"{p_id_list[1][0]}\"
            """
        ))
        else:
            connection.execute(text(
            f"""UPDATE Matchup_Stats SET p1_wins=p1_wins+{stats_dict[p_id_list[1][1]]["Win"]}, p2_wins=p2_wins+{stats_dict[p_id_list[0][1]]["Win"]}, p1_diff =p1_diff+{stats_dict[p_id_list[1][1]]["Diff"]} WHERE p_id_1 =\"{p_id_list[1][0]}\" and p_id_2 =\"{p_id_list[0][0]}\"
            """
        ))
            

        result = connection.execute( text(f"SELECT p_id from Player_Stats where p_name = \"{player}\"") )
        num_results = result.rowcount

        if num_results == 0:
            result = connection.execute( text("SELECT p_id from Player_Stats") )
            p_id = result.rowcount
            

            connection.execute(text(
                    f"INSERT into Player_Stats values({p_id},\'{player}\', {p["Win"]},{p["Losses"]},0,0,0)") )

        else:
            if not post_season:
                connection.execute(text(
                f"""UPDATE Player_Stats SET p_wins=p_wins+{p["Win"]}, p_losses=p_losses+{p["Losses"]} WHERE p_name =\"{player}\"
                """
            ))
                
            elif post_season and not championship:
                connection.execute(text(
                f"""UPDATE Player_Stats SET p_wins=p_wins+{p["Win"]}, p_losses=p_losses+{p["Losses"]}, p_post_season_w=p_post_season_w+{p["Win"]}, p_post_season_l=p_post_season_l+{p["Losses"]} WHERE p_name =\"{player}\"
                """
            ))
            elif post_season and championship:
                connection.execute(text(
                f"""UPDATE Player_Stats SET p_wins=p_wins+{p["Win"]}, p_losses=p_losses+{p["Losses"]}, p_post_season_w=p_post_season_w+{p["Win"]}, p_post_season_l=p_post_season_l+{p["Losses"]}, p_championships=p_championships+{p["Win"]} WHERE p_name =\"{player}\"
                """
            ))


        div_dict = {"Ultra":0,"Dusk":1,"Dawn":2,"Prism":3,"Other":99}
        if div in div_dict:
            connection.execute(text(
                    f"UPDATE Div_Stats SET games_played = games_played+1 WHERE div_name = \"{div}\""
                ))

        else:
            x = 1/0


        p_num = -1
        for player in stats_dict:
            p_num += 1

            for mon in stats_dict[player]["Pokemon"]:
                m = stats_dict[player]["Pokemon"][mon]
                if "’" in mon:
                    mon = mon.replace("’","u2019")
                #print(mon)
                result = connection.execute( text(f"SELECT pkmn_id from PKMN_Stats WHERE pkmn_name = \"{mon}\"") )
                first = result.first()
                if first is None:
                    result = connection.execute( text(f"SELECT pkmn_id from PKMN_Stats WHERE pkmn_name = \"{mon.split("-")[0]}\"") )
                    first = result.first()
                mon_id = first[0]
                div_id = div_dict[div]
                p_id = p_id_list[p_num][0]
                season = int(season)

                result = connection.execute( text(f"SELECT pps_pkmn_id from Poke_Player_Stats where pps_pkmn_id = {mon_id} and pps_coach_id={p_id} and pps_season={season}") )
                num_results = result.rowcount

                if num_results == 0:
        
                    connection.execute(text(
                            f"""INSERT into Poke_Player_Stats values({p_id},{mon_id}, {season},{m["Kills"]},{m["Deaths"]},{m["Dmg_Dealt"]},{m["Dmg_Taken"]}, {m["Switched_out"]},{m["Pkmn_Poisoned"]},{m["Crits"]},{m["Rocks/Spikes_Set"]},{m["Wins"]},{m["Losses"]},{m["Diff"]})"""
                            ))

                else:
                    connection.execute(text(
                    f"""UPDATE Poke_Player_Stats SET pps_kills=pps_kills+{m["Kills"]},pps_deaths=pps_deaths+{m["Deaths"]},pps_dmg_dealt=pps_dmg_dealt+{m["Dmg_Dealt"]},pps_dmg_taken=pps_dmg_taken+{m["Dmg_Taken"]},pps_times_switched=pps_times_switched+{m["Switched_out"]},pps_pkmn_poisoned=pps_pkmn_poisoned+{m["Pkmn_Poisoned"]},pps_crits=pps_crits+{m["Crits"]},pps_rocks_spikes_set=pps_rocks_spikes_set+{m["Rocks/Spikes_Set"]},pps_wins=pps_wins+{m["Wins"]},pps_losses=pps_losses+{m["Losses"]},pps_diff=pps_diff+{m["Diff"]} WHERE pps_coach_id={p_id} and pps_pkmn_id={mon_id} and pps_season={season}
                    """
                ))
                    
                for move in m["Moves_Used"]:
                    result = connection.execute( text(f"SELECT pms_pkmn_id from Poke_Move_Stats where pms_pkmn_id = {mon_id} and pms_move=\"{move}\"") )
                    num_results = result.rowcount

                    if num_results == 0:
            
                        connection.execute(text(
                                f"""INSERT into Poke_Move_Stats values({mon_id},\"{move}\", {m["Moves_Used"][move]})"""
                                ))

                    else:
                        connection.execute(text(
                        f"""UPDATE Poke_Move_Stats SET pms_times_used=pms_times_used+{m["Moves_Used"][move]} WHERE pms_pkmn_id={mon_id} and pms_move={move}
                        """
                    ))
                

                result = connection.execute( text(f"SELECT pds_pkmn_id from Poke_Div_Stats where pds_pkmn_id = {mon_id} and pds_div_id={div_id} and pds_season={season}") )
                num_results = result.rowcount

                if num_results == 0:
        
                    connection.execute(text(
                            f"""INSERT into Poke_Div_Stats values({div_id},{mon_id}, {season},{m["Kills"]},{m["Deaths"]},{m["Dmg_Dealt"]},{m["Dmg_Taken"]}, {m["Switched_out"]},{m["Pkmn_Poisoned"]},{m["Crits"]},{m["Rocks/Spikes_Set"]},{m["Wins"]},{m["Losses"]},{m["Diff"]})"""
                            ))

                else:
                    connection.execute(text(
                    f"""UPDATE Poke_Div_Stats SET pds_kills=pds_kills+{m["Kills"]},pds_deaths=pds_deaths+{m["Deaths"]},pds_dmg_dealt=pds_dmg_dealt+{m["Dmg_Dealt"]},pds_dmg_taken=pds_dmg_taken+{m["Dmg_Taken"]},pds_times_switched=pds_times_switched+{m["Switched_out"]},pds_pkmn_poisoned=pds_pkmn_poisoned+{m["Pkmn_Poisoned"]},pds_crits=pds_crits+{m["Crits"]},pds_rocks_spikes_set=pds_rocks_spikes_set+{m["Rocks/Spikes_Set"]},pds_wins=pds_wins+{m["Wins"]},pds_losses=pds_losses+{m["Losses"]},pds_diff=pds_diff+{m["Diff"]} WHERE pds_div_id={div_id} and pds_pkmn_id={mon_id} and pds_season={season}
                    """
                ))
        connection.commit()


def insert_moves(stats_dict):
    with app.app_context():
        connection = db.session.connection()        
        for player in stats_dict:

            for mon in stats_dict[player]["Pokemon"]:
                
                m = stats_dict[player]["Pokemon"][mon]
                if "’" in mon:
                    mon = mon.replace("’","u2019")
                #print(mon)
                result = connection.execute( text(f"SELECT pkmn_id from PKMN_Stats WHERE pkmn_name = \"{mon}\"") )
                first = result.first()
                if first is None:
                    result = connection.execute( text(f"SELECT pkmn_id from PKMN_Stats WHERE pkmn_name = \"{mon.split("-")[0]}\"") )
                    first = result.first()
                mon_id = first[0]
                    
                for move in m["Moves_Used"]:
                    result = connection.execute( text(f"SELECT pms_pkmn_id from Poke_Move_Stats where pms_pkmn_id = {mon_id} and pms_move=\"{move}\"") )
                    num_results = result.rowcount

                    if num_results == 0:
            
                        connection.execute(text(
                                f"""INSERT into Poke_Move_Stats values({mon_id},\"{move}\", {m["Moves_Used"][move]})"""
                                ))

                    else:
                        connection.execute(text(
                        f"""UPDATE Poke_Move_Stats SET pms_times_used=pms_times_used+{m["Moves_Used"][move]} WHERE pms_pkmn_id={mon_id} and pms_move=\"{move}\"
                        """
                    ))
                        
        connection.commit()

def mass_entry_moves(file_path):
    with open(file_path, "r") as f:
        replays = json.load(f)

        for replay in replays["Regular_Season"]:

            print(replay)

            game_state, stats_dict, log = get_match_stats(replay)

            insert_moves(stats_dict)


        


        for replay in replays["Playoffs"]:

            print(replay)

            game_state, stats_dict, log = get_match_stats(replay)

            insert_moves(stats_dict)

        for replay in replays["Championships"]:

            print(replay)

            game_state, stats_dict, log = get_match_stats(replay)

            insert_moves(stats_dict)

            
def mass_entry(file_path, season):
    with open(file_path, "r") as f:
        replays = json.load(f)

        for div in replays["Regular_Season"]:
            for replay in replays["Regular_Season"][div]:

                with open("replays_in_db.json", "r") as f:
                    replays_in_db = json.load(f)

                    in_db = False
                    for r_type in replays_in_db :
                        if  replay in replays_in_db[r_type]:
                            print("Replay already in database")
                            in_db = True

                    if not in_db:
                        print(replay)
                        try:
                            game_state, stats_dict, log = get_match_stats(replay)

                            db_insert_game(stats_dict,div,season)


                            replays_in_db = {}
                            with open("replays_in_db.json", "r") as f:
                                replays_in_db= json.load(f)

                            
                            replays_in_db["Regular_Season"].append(replay)

                            with open("replays_in_db.json", "w") as f:
                                json.dump(replays_in_db,f,indent=4)

                        except Exception as e:
                            print(e)
                            print("Error when collecting stats")

                            replays_error = {}
                            with open("error_replays_db.json", "r") as f:
                                replays_error= json.load(f)

                            replays_error["Regular_Season"].append(replay)

                            with open("error_replays_db.json", "w") as f:
                                json.dump(replays_error,f,indent=4)


        for div in replays["Playoffs"]:
            for replay in replays["Playoffs"][div]:

                with open("replays_in_db.json", "r") as f:
                    replays_in_db = json.load(f)

                    in_db = False
                    for r_type in replays_in_db :
                        if  replay in replays_in_db[r_type]:
                            print("Replay already in database")
                            in_db = True

                    if not in_db:
                        try:
                            game_state, stats_dict, log = get_match_stats(replay)

                            db_insert_game(stats_dict,div,season,post_season=True)


                            replays_in_db = {}
                            with open("replays_in_db.json", "r") as f:
                                replays_in_db= json.load(f)

                            
                            replays_in_db["Playoffs"].append(replay)

                            with open("replays_in_db.json", "w") as f:
                                json.dump(replays_in_db,f,indent=4)

                        except Exception as e:
                            print(e)
                            print("Error when collecting stats")

                            replays_error = {}
                            with open("error_replays_db.json", "r") as f:
                                replays_error= json.load(f)

                            replays_error["Playoffs"].append(replay)

                            with open("error_replays_db.json", "w") as f:
                                json.dump(replays_error,f,indent=4)


        for div in replays["Championships"]:
            for replay in replays["Championships"][div]:

                with open("replays_in_db.json", "r") as f:
                    replays_in_db = json.load(f)

                    in_db = False
                    for r_type in replays_in_db :
                        if  replay in replays_in_db[r_type]:
                            print("Replay already in database")
                            in_db = True

                    if not in_db:
                        try:
                            game_state, stats_dict, log = get_match_stats(replay)

                            db_insert_game(stats_dict,div,season,post_season=True,championship=True)


                            replays_in_db = {}
                            with open("replays_in_db.json", "r") as f:
                                replays_in_db= json.load(f)

                            
                            replays_in_db["Championships"].append(replay)

                            with open("replays_in_db.json", "w") as f:
                                json.dump(replays_in_db,f,indent=4)

                        except Exception as e:
                            print(e)
                            print("Error when collecting stats")

                            replays_error = {}
                            with open("error_replays_db.json", "r") as f:
                                replays_error= json.load(f)

                            replays_error["Championships"].append(replay)

                            with open("error_replays_db.json", "w") as f:
                                json.dump(replays_error,f,indent=4)


            
def user_input(user_i):

    in_list = user_i.split(" ")

    if in_list[0].lower() == "!cosmogdb":
        if in_list[1].lower() == "insert":
            #should probably make is so only mods can do this

            if in_list[2] == "help":
                return("""Proper formatting for the insert command is 
                       !cosmogdb insert *replay* div=X season=X
                       If in the playoffs add so it looks like
                       !cosmogdb insert *replay* div=X season=X playoffs=True
                       If the championship game add so it looks like
                       !cosmogdb insert *replay* div=X season=X playoffs=True championship=True""")
            else:
                replay = in_list[2]

                with open("replays_in_db.json", "r") as f:
                    replays = json.load(f)
                    for r_type in replays:
                        if  replay in replays[r_type]:
                            return("Replay already in database")
                        else:
                            try:
                                div = in_list[3].split("div=")[1].strip()
                                season = in_list[4].split("season=")[1].strip()
                                game_state, stats_dict, log = get_match_stats(replay)

                                if len(in_list)>=6:
                                    if in_list[5] == "playoff=True":
                                        db_insert_game(stats_dict,div,season,True, False)
                                    elif in_list[5] == "championship=True":
                                        db_insert_game(stats_dict,div,season,False, True)
                                    else:
                                        db_insert_game(stats_dict,div,season)
                                else:
                                    db_insert_game(stats_dict,div,season)


                                replays = {}
                                with open("replays_in_db.json", "r") as f:
                                    replays= json.load(f)

                                if len(in_list)>=6:
                                    if in_list[5] == "playoff=True":
                                        replays["Playoffs"].append(replay)
                                    elif in_list[5] == "championship=True":
                                        replays["Championships"].append(replay)
                                    else:
                                        replays["Regular_Season"].append(replay)
                                else:
                                    replays["Regular_Season"].append(replay)

                                with open("replays_in_db.json", "w") as f:
                                    json.dump(replays,f,indent=4)

                                return("Replay successfully added to database")

                            except:

                                replays = {}
                                with open("error_replays_db.json", "r") as f:
                                    replays= json.load(f)

                                if len(in_list)>=6:
                                    if in_list[4] == "playoff=True":
                                        replays["Playoffs"].append(replay)
                                    elif in_list[4] == "championship=True":
                                        replays["Championships"].append(replay)
                                    else:
                                        replays["Regular_Season"].append(replay)
                                else:
                                    replays["Regular_Season"].append(replay)

                                with open("error_replays_db.json", "w") as f:
                                    json.dump(replays,f,indent=4)

                                return("Error when collecting stats")

        elif in_list[1].lower() == "query":

            with app.app_context():
                connection = db.session.connection()

                if "by" in in_list[2]:
                    by = in_list[2].split("by=")[1]

                    if by == "Poke_Player":

                        if in_list[3] == "help":
                            return("""This gets stats for each unqiue pokemon and player combination
                                   Example: !cosmogdb query by=Poke_Player stat=dmg_dealt season=8
                                   Replace the stat with the stat you want to sort by, this will only give the top 10 results. Replace the season number with the season you want stats from
                                   The current stats you can query are kills, deaths, dmg_dealt, dmg_taken, times_switched, pkmn_poisoned, crits, rocks_spikes_set,wins,losses, and diff""")
                        
                        query_stat = in_list[3].split("stat=")[1]
                        season = int(in_list[4].split("season=")[1])
                        result = connection.execute( text(f"""SELECT p_name,pkmn_name,pps_{query_stat} from Poke_Player_Stats natural join Player_Stats,PKMN_stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_coach_id = Player_Stats.p_id and Poke_Player_Stats.pps_pkmn_id = PKMN_Stats.pkmn_id ORDER BY pps_{query_stat} DESC""") )
                        
                        return_string = "```"
                        i = 1
                        for row in result:
                            if i<=10:
                                return_string += (str(i) + " " + row[0] + "'s " + row[1] + ": " + str(row[2]) + "\n")
                                i+=1

                        return_string += "```"
                        return return_string
                    
                    if by == "Player":
                        if in_list[3] == "help":
                            return("""This gets stats for each player
                                   Example: !cosmogdb query by=Player stat=times_switched season=8
                                   Alternatively if you want the stats on a specific player try: !cosmogdb query by=Player stat=dmg_dealt season=8 player=lilqwispy
                                   Replace the stat with the stat you want to sort by, this will only give the top 10 results. Replace the season number with the season you want stats from
                                   The current stats you can query are kills, deaths, dmg_dealt, dmg_taken, times_switched, pkmn_poisoned, crits, rocks_spikes_set,wins,losses, and diff""")

                        if len(in_list) ==6:

                            query_stat = in_list[3].split("stat=")[1]
                            season = int(in_list[4].split("season=")[1])
                            player = in_list[5].split("player=")[1]
                            result = connection.execute( text(f"""SELECT p_name,pkmn_name,pps_kills,pps_deaths,pps_dmg_dealt,pps_dmg_taken,pps_times_switched,pps_pkmn_poisoned,pps_crits,pps_rocks_spikes_set,pps_wins,pps_losses,pps_diff from Poke_Player_Stats natural join Player_Stats,PKMN_stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_coach_id = Player_Stats.p_id and Poke_Player_Stats.pps_pkmn_id = PKMN_Stats.pkmn_id and Player_Stats.p_name = \"{player}\" ORDER BY pps_{query_stat} DESC""") )
                            return_string = "```"

                            
                            i = 1
                            totals = [0,0,0,0,0,0,0,0,0,0,0]

                            return_string += ((str("") + " " + str("")).ljust(17) + " || " + str("K").ljust(3) + " || " +str("D").ljust(3) + " || " +str("dealt").ljust(8) + " || " +str("taken").ljust(8) + " || " +str("switch").ljust(8) + " || " +str("psn").ljust(8) + " || " +str("crit").ljust(5) + " || " +str("rocks").ljust(6) + " || " +str("W").ljust(3) + " || " +str("L").ljust(3) + " || " +str("Dif").ljust(3) +"\n")
                            for row in result:
                                if i<=15:
                                    return_string += ((str(i) + " " + str(row[1])).ljust(17) + " || " + str(row[2]).ljust(3) + " || " +str(row[3]).ljust(3) + " || " +str(row[4]).ljust(8) + " || " +str(row[5]).ljust(8) + " || " +str(row[6]).ljust(8) + " || " +str(row[7]).ljust(8) + " || " +str(row[8]).ljust(5) + " || " +str(row[9]).ljust(6) + " || " +str(row[10]).ljust(3) + " || " +str(row[11]).ljust(3) + " || " +str(row[12]).ljust(3) +"\n")
                                    i+=1
                                

                                j=0
                                for stat in row[2:]:
                                    totals[j] += stat
                                    j+=1

                            if i == 15:
                                return_string += "...\n"
                            return_string += ((str(i) + " " + str("Total")).ljust(17) + " || " + str(totals[0]).ljust(3) + " || " +str(totals[1]).ljust(3) + " || " +str(totals[2]).ljust(8) + " || " +str(totals[3]).ljust(8) + " || " +str(totals[4]).ljust(8) + " || " +str(totals[5]).ljust(8) + " || " +str(totals[6]).ljust(5) + " || " +str(totals[7]).ljust(6) + " || " +str(totals[8]).ljust(3) + " || " +str(totals[9]).ljust(3) + " || " +str(totals[10]).ljust(3) +"\n")
                            
                            return_string += "```"
                            return return_string

                        
                        query_stat = in_list[3].split("stat=")[1]
                        season = int(in_list[4].split("season=")[1])
                        result = connection.execute( text(f"""SELECT p_name, sum(pps_{query_stat}) as sum_stat from Poke_Player_Stats natural join Player_Stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_coach_id = Player_Stats.p_id GROUP BY p_name ORDER BY sum_stat DESC""") )                    
                        return_string = "```"
                        i = 1
                        for row in result:
                            if i<=10:
                                return_string += (str(i) + " " + row[0] + ": " + str(row[1]) + "\n")
                                i+=1

                        return_string += "```"
                        return return_string
                    
                    if by == "Div":

                        if in_list[3] == "help":
                            return("""This gets stats for each divison
                                   Example: !cosmogdb query by=Div stat=rocks_spikes_set season=8
                                   Replace the stat with the stat you want to sort by, this should give 1 result per divison. Replace the season number with the season you want stats from
                                   The current stats you can query are kills, deaths, dmg_dealt, dmg_taken, times_switched, pkmn_poisoned, crits, rocks_spikes_set,wins,losses, and diff""")
                        
                        
                        query_stat = in_list[3].split("stat=")[1]
                        season = int(in_list[4].split("season=")[1])
                        result = connection.execute( text(f"""SELECT div_name, sum(pds_{query_stat}) as sum_stat from Poke_Div_Stats natural join Div_Stats where Poke_Div_Stats.pds_season = {season} and Poke_Div_Stats.pds_div_id = Div_Stats.div_id GROUP BY div_name ORDER BY sum_stat DESC""") )                    
                        return_string = "```"
                        i = 1
                        for row in result:
                            if i<=4:
                                return_string += (str(i) + " " + row[0] + ": " + str(row[1]) + "\n")
                                i+=1

                        return_string += "```"
                        return return_string
                    
                    if by == "Poke":

                        if in_list[3] == "help":
                            return("""This gets the sum of stats over all players that drafted the pokemon
                                   Example: !cosmogdb query by=Poke stat=dmg_dealt season=8
                                   Replace the stat with the stat you want to sort by, this will only give the top 10 results. Replace the season number with the season you want stats from
                                   The current stats you can query are kills, deaths, dmg_dealt, dmg_taken, times_switched, pkmn_poisoned, crits, rocks_spikes_set,wins,losses, and diff""")
                        
                        
                        query_stat = in_list[3].split("stat=")[1]
                        season = int(in_list[4].split("season=")[1])
                        result = connection.execute( text(f"""SELECT pkmn_name, sum(pps_{query_stat}) as sum_stat from Poke_Player_Stats natural join PKMN_Stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_pkmn_id = PKMN_Stats.pkmn_id GROUP BY pkmn_name ORDER BY sum_stat DESC""") )                    
                        return_string = "```"
                        i = 1
                        for row in result:
                            if i<=10:
                                return_string += (str(i) + " " + row[0] + ": " + str(row[1]) + "\n")
                                i+=1

                        return_string += "```"
                        return return_string
                    
                    if by == "Move":

                        if in_list[3] == "help":
                            return("""This gets the 8 most popular moves used by a pokemon if you want some inspiration
                                   Example: !cosmogdb query by=Move pkmn=Entei
                                   replace Entei with the pokemon that you want to get info on
                                   Due to the limitations of the database (my coding ability) all pokemon are split up by forms so if Mimikyu doesn't give good results try Mimikyu-Busted or whatever the strange form is for the mon you are looking for""")
                        
                        
                        pkmn = in_list[3].split("pkmn=")[1]
                        result = connection.execute( text(f"""SELECT pkmn_name, pms_move,pms_times_used from Poke_Move_Stats natural join PKMN_Stats where PKMN_Stats.pkmn_id = Poke_Move_Stats.pms_pkmn_id and PKMN_Stats.pkmn_name = \"{pkmn}\" ORDER BY pms_times_used DESC""") )                    
                        return_string = "```"
                        i = 1
                        for row in result:
                            if i<=8:
                                return_string += (str(i) + " " + row[1] + ": " + str(row[2]) + "\n")
                                i+=1

                        return_string += "```"
                        return return_string
                    
                    if by == "Type":

                        if in_list[3] == "help":
                            return("""This gets the stats of a specific type of pokemon
                                   Example: !cosmogdb query by=Type stat=dmg_dealt season=8 type=Electric
                                   Replace the stat with the stat you want to sort by, this will only give the top 10 results. Replace the season number with the season you want stats from
                                   The current stats you can query are kills, deaths, dmg_dealt, dmg_taken, times_switched, pkmn_poisoned, crits, rocks_spikes_set,wins,losses, and diff""")
                        
                        query_stat = in_list[3].split("stat=")[1]
                        season = int(in_list[4].split("season=")[1])
                        mon_type = in_list[5].split("type=")[1]
                        result = connection.execute( text(f"""SELECT pkmn_name,sum(pps_{query_stat}) as sum_stat from Poke_Player_Stats natural join PKMN_stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_pkmn_id = PKMN_Stats.pkmn_id and (PKMN_Stats.type1 = \"{mon_type}\" or PKMN_Stats.type2 = \"{mon_type}\") GROUP BY pps_pkmn_id ORDER BY sum_stat DESC""") )
                        
                        return_string = "```"
                        i = 1
                        for row in result:
                            if i<=10:
                                return_string += (str(i) + " " + row[0] + ": " + str(row[1]) + "\n")
                                i+=1

                        return_string += "```"
                        return return_string
                    
                elif in_list[2] == "raw":
                    #This should probably also be mod only
                    result = connection.execute( text(in_list[3]) )                    
                    return_string = "```"
                    i = 1
                    for row in result:
                        if i<=10:
                            return_string += (str(i) + " " + row[0] + ": " + str(row[1]) + "\n")
                            i+=1

                    return_string += "```"
                    return return_string
                
                elif in_list[2] == "help":
                    return("""This is the main way to get information from cosmog db.
                           You can currently get stats on: Poke_Player, Player, Poke, Div, Move, and Type
                           Try !cosmogdb query by=*what you want stats on* help to find out more.""")
                    

        elif in_list[1].lower() == "help":
            return("""Current list of cosmog db commands:
                   query
                   try !cosmogdb *command* help for more detailed information
                   """)
        return("Command Not Recognized")
        

if __name__ == "__main__":
    while(1):
        x = input()
        user_input(x)




    
