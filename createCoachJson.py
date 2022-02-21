import json

#list in the form ("CoachName", "TeamName")
COACH = 0
TEAM = 1

coaches = [("PurpleDolphin","Hammerlocke Drednaw"), ("Galenskog","Core Enfourzer"),("Casey","Goldenrod Gliscor"),("LittleBigs672", "Rain City Rillaboom"),
            ("HGC", "Caracas Carracostas"),("Sand Castle","Azalea Galvantula"),("Mmattus","Wedgehurst Gogoat"),("Coach Oak","Iki Town Incineroar"),
            ("PotatoZ","Rotom Washington Wizards"),("Froski 101","Hearthome Honchkrow"), ("Yueku","Possessed Pumpkaboos"),("YungBisharp", "Driftveil Darkrai"),
            ("I Miss Dad","Vice City Voltage"),("AliceSabrina","Canberran Charmanders"),("CousinZinny", "Celestic Chimchars"),("CatsRuleTheDumb","Flight Club"),
            ("SpiderRyno","Stow-on-Side Gurdurr"),("HawaiianShaymin","The Spirit Archers"),("Lightning", "New England Ninetales"), ("Chandy","Ok Boomer Chandelures"),
            ("AceHarm555", "Melbourne Magnezonez"), ("TebowTime", "Aurora Alolan Vulpix"), ("FistToYourDoom", "Cult of Character Limit"), ("Gradual", "Sunset Solrocks"),
            ("Tedward","Glimwood Golurk"),("TangelaBoots","Twinleaf Town Tangela"), ("Pluto","Village Bridge Volcarona"), ("Blind Messiah", "Vienna Vibe Check"),
            ("PastaSupper", "St. John's Sandiles"),("RainbowDonutCat","Palm Beach Pults"),("Triviess","Snowpoint Sylveons"),("Bassrman","Dewford Doublade")]
stats = {}
with open("coachStats.json", "r") as file:
    stats = json.load(file)

    for pair in coaches:
        if(pair[COACH] not in stats.keys()):
            stats[pair[COACH]] = {"Team Name": pair[TEAM], "Wins":0, "Losses":0, "Differential":0, "Pokemon":{"Example":{"Kills": 0, "Deaths": 0, "Games Played":0, "Games Eligible":0}}, "vs":{"ExampleCoach": {"Replays":["https...."], "Wins":0, "Losses":0,"Differential":0}}}


with open("coachStats.json", "w") as file:
    json.dump(stats,file,indent=4)
