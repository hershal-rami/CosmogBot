import requests
import json

def get_battle_log(link):
    result = requests.get(link)
    source = result.content
    print(source)
    json_ver = json.loads(source)
    json_ver["log"] = json_ver["log"].split("\n")
    for line in json_ver["log"]:
        print(line)


if __name__ == "__main__":
    replay = "https://replay.pokemonshowdown.com/sports-gen8nationaldexdraft-731995.json"
    get_battle_log(replay)
