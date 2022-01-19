# CosmogBot
CosmogBot is a Discord bot for the Mt. Battle Tournament League, helping manage and organize the league's drafts

# Setup
Install Python version >= 3.5.3 and run `python3 -m pip install -U discord.py`

Open ~/.bashrc and add `export DISCORD_TOKEN={your_key_here}` replacing that text with the key.
Then restart your shell application and type `env | grep "DISCORD_TOKEN"`. It should print the key.

# Running the bot
Once you have your token variable set in your local environment, simply run `python3 bot.py` and the bot will go online!

# Goals:
-pull team roles from spreadsheet and @ them to display schedule each week
-pokedex data, showdown API type stuff
-keep track of which coaches are active in a given season
-keep track of which matches have been completed or not
-keep database of each players replays?
-grab k/d statistics from Porygon and update spreadsheet
-calculate kill leaders and update spreadsheet (this script exists but can be integrated into bot functionality)
-can update differential/standings too if desired
-make a thread for each postgame to avoid spoilers and contain conversation?
-host bot on not my laptop

# Resources:
https://realpython.com/how-to-make-a-discord-bot-python/
https://github.com/Rapptz/discord.py/tree/v1.7.3/examples
https://discordpy.readthedocs.io/en/stable/index.html
https://discordpy.readthedocs.io/en/stable/faq.html