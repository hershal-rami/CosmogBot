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

import numpy as np

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

#list of banned pokemon
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


DONT_MOVE_CHECK = ["farfetchu2019d"]
def remove_non_alpha(input_str):
    output_str = (''.join([i for i in input_str if i.isalnum()])).lower()
    return output_str

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
                        f"""UPDATE Poke_Move_Stats SET pms_times_used=pms_times_used+{m["Moves_Used"][move]} WHERE pms_pkmn_id={mon_id} and pms_move=\"{move}\""""
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

        for div in replays["Regular_Season"]:
            for replay in replays["Regular_Season"][div]:

                print(replay)

                game_state, stats_dict, log = get_match_stats(replay)

                insert_moves(stats_dict)


        


        for div in replays["Playoffs"]:
            for replay in replays["Playoffs"][div]:

                print(replay)

                game_state, stats_dict, log = get_match_stats(replay)

                insert_moves(stats_dict)

        for div in replays["Championships"]:
            for replay in replays["Championships"][div]:

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
                        result = connection.execute( text(f"""SELECT p_name,pkmn_name,pps_{query_stat} from Poke_Player_Stats natural join Player_Stats,PKMN_Stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_coach_id = Player_Stats.p_id and Poke_Player_Stats.pps_pkmn_id = PKMN_Stats.pkmn_id ORDER BY pps_{query_stat} DESC""") )
                        
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
                            result = connection.execute( text(f"""SELECT p_name,pkmn_name,pps_kills,pps_deaths,pps_dmg_dealt,pps_dmg_taken,pps_times_switched,pps_pkmn_poisoned,pps_crits,pps_rocks_spikes_set,pps_wins,pps_losses,pps_diff from Poke_Player_Stats natural join Player_Stats,PKMN_Stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_coach_id = Player_Stats.p_id and Poke_Player_Stats.pps_pkmn_id = PKMN_Stats.pkmn_id and Player_Stats.p_name = \"{player}\" ORDER BY pps_{query_stat} DESC""") )
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
                        result = connection.execute( text(f"""SELECT pkmn_name,sum(pps_{query_stat}) as sum_stat from Poke_Player_Stats natural join PKMN_Stats where Poke_Player_Stats.pps_season = {season} and Poke_Player_Stats.pps_pkmn_id = PKMN_Stats.pkmn_id and (PKMN_Stats.type1 = \"{mon_type}\" or PKMN_Stats.type2 = \"{mon_type}\") GROUP BY pps_pkmn_id ORDER BY sum_stat DESC""") )
                        
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
    
    elif in_list[0].lower() == "!cosmogdraft":

        with app.app_context():
            connection = db.session.connection()

            if in_list[1].lower() == "teamhelp":

                filter_stat = None
                filter_value = None
                filter_greater = False
                filter_less = False

                filter_move=False
                filter_move_list = []
                filter_and = False
                filter_or = True
                
                with open("Pokemon_Info/learnsets.json") as moves:
                        learnsets = json.load(moves)

                filter_type = None
                filter_type_multiple = []
                filter_type_and = True
                filter_type_or = False

                low_tier_mode = False

                if "filter_stat" in user_i:
                    for arg in in_list:
                        if "filter_stat" in arg:

                            if "<" in arg:
                                filter_less =True
                                filter_value = int(arg.split("<")[1].strip())
                            else:
                                filter_greater = True
                                filter_value = int(arg.split(">")[1].strip())
                            
                            if "hp" in arg:
                                filter_stat="hp"
                            if "atk" in arg:
                                filter_stat="atk"
                            if "def" in arg:
                                filter_stat="def"
                            if "spatk" in arg:
                                filter_stat="spatk"
                            if "spdef" in arg:
                                filter_stat="spdef"
                            if "spe" in arg:
                                filter_stat="spe"

                if "filter_move" in user_i:

                    filter_move=True
                    if "filter_move_mode=and" in user_i:
                        filter_and=True
                        filter_or = False
                    
                    for move in user_i.split("filter_move=[")[1].split("]")[0].split(","):
                        filter_move_list.append(move.strip())

                if "filter_type" in user_i:

                    if "filter_type_mode=or" in user_i:
                        filter_type_and = False
                        filter_type_or = True

                    if "filter_type=[" in user_i:
                        for p_type in user_i.split("filter_type=[")[1].split("]")[0].split(","):
                            filter_type_multiple.append(p_type.strip().lower())

                    else:
                        filter_type = user_i.split("filter_type=")[1].split(" ")[0].strip().lower()


                if "low_tier_mode=True" in user_i:
                    low_tier_mode=True
                
                if "team=[" in user_i:
                    team = user_i.split("team=[")[1].split("]")[0].split(",")

                    hp = []
                    atk = []
                    defen = []
                    spatk = []
                    spdef = []
                    spe = []

                    weak = []
                    res = []
                    
                    rocks = False
                    removal = False
                    utility_score_0 = 0
                    for mon in team:
                        result = connection.execute( text(f"""SELECT type1,type2,HP,ATK,DEF,SPATK,SPDEF,SPE from PKMN_Stats where pkmn_name=\"{mon.strip()}\"""") )
                        for row in result:

                            hp.append(int(row[2]))
                            atk.append(int(row[3]))
                            defen.append(int(row[4]))
                            spatk.append(int(row[5]))
                            spdef.append(int(row[6]))
                            spe.append(int(row[7]))

                            if row[1] == None:
                                type_effective = np.array(WEAKNESS[row[0]]) * np.array(RESISTANCE[row[0]])
                            else:
                                type_effective = np.array(WEAKNESS[row[0]]) * np.array(RESISTANCE[row[0]]) * np.array(WEAKNESS[row[1]]) * np.array(RESISTANCE[row[1]])

                            #set everything this mon is not weak to to 0
                            w = np.maximum(type_effective,1).astype(int)
                            w[w == 1] = 0
                            weak.append(w)

                            #boolean vector 1 if resists that type 0 if not
                            res.append((type_effective < 1).astype(int))


                            #try to look for utility in the pokemon's moveset
                            utility_moves = ["Spikes", "Toxic Spikes", "Sticky Webs", "Wish", "Haze", "Clear Smog", "Will-o-Wisp", "Tailwind", "Reflect", "Light Screen"]
                            
                            mon = remove_non_alpha(mon.strip().lower())

                            if mon[-4:] == "mega":
                                mon = mon[:-4]

                            if mon in learnsets:
                                
                                if not rocks and remove_non_alpha("Stealth Rock").lower() in learnsets[mon]:
                                    utility_score_0 += 5
                                    rocks= True
                                elif rocks and remove_non_alpha("Stealth Rock").lower() in learnsets[mon]:
                                    utility_score_0 += 1

                                if not removal and (remove_non_alpha("Defog").lower() in learnsets[mon] or remove_non_alpha("Rapid Spin").lower() in learnsets[mon]):
                                    utility_score_0 += 5
                                    rocks= True
                                elif removal and (remove_non_alpha("Defog").lower() in learnsets[mon] or remove_non_alpha("Rapid Spin").lower() in learnsets[mon]):
                                    utility_score_0 += 1

                                for move in utility_moves:

                                    if remove_non_alpha(move).lower() in learnsets[mon]:
                                        utility_score_0 +=1


                    total_res = np.sum(np.array(res),axis = 0)

                    #find the sum of the weakenesses, subtract the resistances turn anything not weak to overall to 0
                    total_weak = (np.sum(np.array(weak), axis=0) - 2 * total_res)
                    total_weak[total_weak <=0] = 0
                    
                    #weak score is the squared loss of the total weakness vector (want to minimize)
                    weak_score_0 = np.sum(total_weak**2)
                    
                    #res score is the number of types we have less than 2 resistances to (want to minimize)
                    res_score_0 = np.sum(total_res < 2)

                    #stat_score_0 = 0

                    """
                    #based on average stats of the OU tier in 2022 about equal to 90, 100, 95, 95, 90, 90
                    #takes how far away you are from meeting the bar in each stat and adds it together (want to minimize)
                    if np.mean(hp) < 90:
                        stat_score_0 += (90 - np.mean(hp))**3
                    if np.mean(atk) < 100:
                        stat_score_0 += (100 - np.mean(atk))**3
                    if np.mean(defen) < 95:
                        stat_score_0 += (95 - np.mean(defen))**3
                    if np.mean(spatk) < 95:
                        stat_score_0 += (95 - np.mean(spatk))**3
                    if np.mean(spdef) < 90:
                        stat_score_0 += (90 - np.mean(spdef))**3
                    if np.mean(spe) < 90:
                        stat_score_0 += (90 - np.mean(spe))**3
                    """
                    #instead of doing that which is dumb, lets try to make a balanced team by traying to minimize the squared difference between ATK and SPATK and DEF and SPDEF
                    #and maximize speed

                    def_score_0 = (np.mean(defen) - np.mean(spdef)) ** 2
                    atk_score_0 = (np.mean(atk) - np.mean(spatk)) ** 2
                    spe_score = np.mean(spe)

                    #print(stat_score_0)
                    #print(weak_score_0)
                    #print(res_score_0)

                    team_strength_score_0 = -0.3 * weak_score_0 - 0.6*res_score_0 + 0.5*utility_score_0 - 0.5 * def_score_0 - 0.5 * atk_score_0 + spe_score

                    #print(team_strength_score_0)

                    pkmn_res = []

                    #go through each pokemon and calculate the strength score as if the pokemon was added
                    result = connection.execute( text(f"""SELECT type1,type2,HP,ATK,DEF,SPATK,SPDEF,SPE, pkmn_name from PKMN_Stats""") )
                    for row in result:

                        include = True
                        if row[8] in BANNED:
                            include = False

                        if filter_stat and include:

                            if filter_less:

                                if filter_stat == "hp":
                                    if int(row[2]) >= filter_value:
                                        include = False
                                if filter_stat == "atk":
                                    if int(row[3]) >= filter_value:
                                        include = False
                                if filter_stat == "def":
                                    if int(row[4]) >= filter_value:
                                        include = False
                                if filter_stat == "spatk":
                                    if int(row[5]) >= filter_value:
                                        include = False
                                if filter_stat == "spdef":
                                    if int(row[6]) >= filter_value:
                                        include = False
                                if filter_stat == "spe":
                                    if int(row[7]) >= filter_value:
                                        include = False

                            elif filter_greater:

                                if filter_stat == "hp":
                                    if int(row[2]) <= filter_value:
                                        include = False
                                if filter_stat == "atk":
                                    if int(row[3]) <= filter_value:
                                        include = False
                                if filter_stat == "def":
                                    if int(row[4]) <= filter_value:
                                        include = False
                                if filter_stat == "spatk":
                                    if int(row[5]) <= filter_value:
                                        include = False
                                if filter_stat == "spdef":
                                    if int(row[6]) <= filter_value:
                                        include = False
                                if filter_stat == "spe":
                                    if int(row[7]) <= filter_value:
                                        include = False

                        if filter_move and include:

                            try:

                                if filter_and:
                                    for move in filter_move_list:
                                        mon = remove_non_alpha(row[8])

                                        if mon[-4:] == "mega":
                                            mon = mon[:-4]

                                        if mon not in learnsets:
                                            include=False
                                        if remove_non_alpha(move).lower() not in learnsets[mon]:
                                            include=False

                                if filter_or:

                                    include=False
                                    for move in filter_move_list:
                                        mon = remove_non_alpha(row[8])

                                        if mon[-4:] == "mega":
                                            mon = mon[:-4]

                                    
                                        if mon not in learnsets:
                                            
                                        
                                            include=False
                                        
                                        if remove_non_alpha(move).lower() in learnsets[mon]:
                                        
                                            include=True

                            except:
                                include=False

                        if (filter_type or filter_type_multiple) and include:

                            if filter_type_and:
                                if not filter_type_multiple:
                                    if row[1] == None:
                                        if row[0].lower() != filter_type:
                                            include = False

                                    else:
                                        if row[0].lower() != filter_type and row[1] != filter_type:
                                            include = False
                                else:
                                    
                                    if row[1] == None and len(filter_type_multiple) == 2:
                                        include=False
                                    else:
                                        if (row[1].lower() not in filter_type_multiple) or (row[0].lower() not in filter_type_multiple):
                                            include=False

                            elif filter_type_or:
                                
                                if not filter_type_multiple:
                                    if row[1] == None:
                                        if row[0].lower() != filter_type:
                                            include = False

                                    else:
                                        if row[0].lower() != filter_type and row[1] != filter_type:
                                            include = False

                                else:
                                    if row[1] == None:
                                        if row[0].lower() not in filter_type_multiple:
                                            include = False

                                    else:
                                        if row[0].lower() not in filter_type_multiple and row[1] not in filter_type_multiple:
                                            include = False


                        require_increase = True
                        if low_tier_mode:
                            if int(row[2]) + int(row[3]) + int(row[4]) + int(row[5]) + int(row[6]) + int(row[7]) > 525:
                                include=False
                            require_increase = False

                        
                        if include:

                            hp_temp = hp + [int(row[2])]
                            atk_temp = atk + [int(row[3])]
                            defen_temp = defen + [int(row[4])]
                            spatk_temp = spatk + [int(row[5])]
                            spdef_temp = spdef + [int(row[6])]
                            spe_temp = spe + [int(row[7])]

                            if row[1] == None:
                                type_effective = np.array(WEAKNESS[row[0]]) * np.array(RESISTANCE[row[0]])
                            else:
                                type_effective = np.array(WEAKNESS[row[0]]) * np.array(RESISTANCE[row[0]]) * np.array(WEAKNESS[row[1]]) * np.array(RESISTANCE[row[1]])


                            #set everything this mon is not weak to to 0
                            w = np.maximum(type_effective,1).astype(int)
                            w[w == 1] = 0
                            weak_temp = weak + [w]

                            #boolean vector 1 if resists that type 0 if not
                            res_temp = res + [(type_effective < 1).astype(int)]

                            #try to look for utility in the pokemon's moveset
                            utility_moves = ["Spikes", "Toxic Spikes", "Sticky Webs", "Wish", "Haze", "Clear Smog", "Will-o-Wisp", "Tailwind", "Reflect", "Light Screen"]
                            
                            utility_score_temp = utility_score_0
                            mon = remove_non_alpha(row[8].strip().lower())

                            if mon[-4:] == "mega":
                                mon = mon[:-4]


                            if mon in learnsets:
                                
                                if not rocks and remove_non_alpha("Stealth Rock").lower() in learnsets[mon]:
                                    utility_score_temp += 5
                                elif rocks and remove_non_alpha("Stealth Rock").lower() in learnsets[mon]:
                                    utility_score_temp += 1

                                if not removal and (remove_non_alpha("Defog").lower() in learnsets[mon] or remove_non_alpha("Rapid Spin").lower() in learnsets[mon]):
                                    utility_score_temp += 5
                                elif removal and (remove_non_alpha("Defog").lower() in learnsets[mon] or remove_non_alpha("Rapid Spin").lower() in learnsets[mon]):
                                    utility_score_temp += 1

                                for move in utility_moves:

                                    if remove_non_alpha(move).lower() in learnsets[mon]:
                                        utility_score_temp +=1

                            total_res = np.sum(np.array(res_temp),axis = 0)

                            #find the sum of the weakenesses, subtract the resistances turn anything not weak to overall to 0
                            total_weak = (np.sum(np.array(weak_temp), axis=0) - 2 * total_res)
                            total_weak[total_weak <=0] = 0
                            
                            #weak score is the squared loss of the total weakness vector (want to minimize)
                            weak_score_new = np.sum(total_weak**2)
                            
                            #res score is the number of types we have less than 2 resistances to (want to minimize)
                            res_score_new = np.sum(total_res < 2)

                            stat_score_new = 0

                            """
                            #based on average stats of the OU tier in 2022 about equal to 90, 100, 95, 95, 90, 90
                            #takes how far away you are from meeting the bar in each stat and adds it together (want to minimize)
                            if np.mean(hp_temp) < 90:
                                stat_score_new += (90 - np.mean(hp_temp))**3
                            if np.mean(atk_temp) < 100:
                                stat_score_new += (100 - np.mean(atk_temp))**3
                            if np.mean(defen_temp) < 95:
                                stat_score_new += (95 - np.mean(defen_temp))**3
                            if np.mean(spatk_temp) < 95:
                                stat_score_new += (95 - np.mean(spatk_temp))**3
                            if np.mean(spdef_temp) < 90:
                                stat_score_new += (90 - np.mean(spdef_temp))**3
                            if np.mean(spe_temp) < 90:
                                stat_score_new += (90 - np.mean(spe_temp))**3

                            """

                            #instead of doing that which is dumb, lets try to make a balanced team by traying to minimize the squared difference between ATK and SPATK and DEF and SPDEF
                            #and maximize speed

                            def_score_new = (np.mean(defen_temp) - np.mean(spdef_temp)) ** 2
                            atk_score_new = (np.mean(atk_temp) - np.mean(spatk_temp)) ** 2
                            spe_score_new = np.mean(spe)

                            #print(stat_score_0)
                            #print(weak_score_0)
                            #print(res_score_0)

                            team_strength_score_new = -0.3 * weak_score_new - 0.6*res_score_new + 0.5*utility_score_temp- 0.5 * def_score_new - 0.5 * atk_score_new + spe_score_new


                            #only if the pokemon makes an improvement keep it or we are in low tier mode
                            if team_strength_score_new < team_strength_score_0 or not require_increase:
                                #append the name of the pokemon and how much it improves on the strength score (want to maximize this)
                                pkmn_res.append((row[8], team_strength_score_0 - team_strength_score_new))

                    sorted_res = sorted(pkmn_res, key=lambda x:x[1],reverse=True)

                    if(len(sorted_res) >= 15):
                        print("===================================================")
                        print("| " + "Pokemon".ljust(20) + "|| " + "Increase in Team Score".ljust(25) + "|")
                        print("===================================================")
                        for i in range(15):
                            print("| " + sorted_res[i][0].ljust(20) + "|| " + str(sorted_res[i][1]).ljust(25) + "|")
                        print("===================================================")
                    else:
                        print("===================================================")
                        print("| " + "Pokemon".ljust(20) + "|| " + "Increase in Team Score".ljust(25) + "|")
                        print("===================================================")
                        for i in range(len(sorted_res)):
                            print("| " + sorted_res[i][0].ljust(20) + "|| " + str(sorted_res[i][1]).ljust(25) + "|")
                        print("===================================================")

                        

        return("Command Not Recognized")
    

def json_pkmn_characteristics():

    with open("./data/Pokemon_Feature_Data.json", "w") as wfile:

        json_write = {}

        with app.app_context():
                connection = db.session.connection()

            
                #go through each pokemon and calculate the strength score as if the pokemon was added
                result = connection.execute( text(f"""SELECT type1,type2,HP,ATK,DEF,SPATK,SPDEF,SPE, pkmn_name from PKMN_Stats""") )
                for row in result:

                    include = True
                    if row[8] in BANNED:
                        include = False
                    
                    if include:

                        hp = int(row[2])
                        atk= int(row[3])
                        defen = int(row[4])
                        spatk = int(row[5])
                        spdef = int(row[6])
                        spe = int(row[7])

                        type1 = row[0]
                        type2 = row[1]

                        type_effective = []
                        if row[1] == None:
                            type_effective = np.array(WEAKNESS[row[0]]) * np.array(RESISTANCE[row[0]])
                        else:
                            type_effective = np.array(WEAKNESS[row[0]]) * np.array(RESISTANCE[row[0]]) * np.array(WEAKNESS[row[1]]) * np.array(RESISTANCE[row[1]])

                        #try to look for utility in the pokemon's moveset
                        utility_moves = ["Stealth Rock", "Defog", "Rapid Spin", "Spikes", "Toxic Spikes", "Sticky Webs", "Wish", "Haze", "Clear Smog", "Will-o-Wisp", "Tailwind", "Reflect", "Light Screen"]
                        
                        utility_score_temp = 0
                        mon = remove_non_alpha(row[8].strip().lower())

                        if mon[-4:] == "mega":
                            mon = mon[:-4]

                        learnsets = {}
                        with open("Pokemon_Info/learnsets.json") as moves:
                            learnsets = json.load(moves)

                        mon_u_moves = []


                        if mon in learnsets:

                            for move in utility_moves:

                                if remove_non_alpha(move).lower() in learnsets[mon]:
                                    mon_u_moves.append(move)

                        name = row[8]

                        json_write[name] = {"STATS":[hp,atk,defen,spatk,spdef,spe], "TYPE":[type1,type2], "TYPE_EFFECTIVE":list(type_effective.astype(float)), "UTILITY":mon_u_moves}

                    

        json.dump(json_write,wfile,indent=4)

if __name__ == "__main__":

    """
    setup()
    mass_entry_moves("mass_entry.json")
    mass_entry("mass_entry.json", 8)
    """
    

    """
    while(1):
        x = input()
        print(user_input(x))
    """
    json_pkmn_characteristics()
        




    
