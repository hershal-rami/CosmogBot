# CosmogBot
CosmogBot is a Discord bot for the Mt. Battle Tournament League, helping manage and organize the league's drafts

# Setup
Install Python version >= 3.5.3

Run the following commands:
    `python3 -m pip install -U discord.py`

    `pip install pandas`
    
    `pip install gspread`
    
    `pip install gspread_formatting`

Open ~/.bashrc and add `export DISCORD_TOKEN={your_key_here}` replacing that text with the key.
Then restart your shell application and type `env | grep "DISCORD_TOKEN"`. It should print the key.

# Running the bot
Once you have your token variable set in your local environment, simply run `python3 bot.py` and the bot will go online!

# Goals:
-review doc carefully for typos and additional 's'

-also check for pokemon name schemes: "grimer-a" vs "grimer-alola"

-fix update match results code to account for spreadsheet changes

-k/d and kill leaders:

    -keep track of each pokemon's k/d (in a spreadsheet)
    
    -update k/d statistics when updating match results
    
    -implement function to calculate all time kill leaders and update spreadsheet
    
    -implement command to display all time kill leaders
-categorize commands (using cogs so that in .help the commands are labelled instead of "no category")

-require or not require permissions for specific commands to prevent abuse

-add error handling (upon error send a descriptive message in the channel so the user knows the issue, ex not having admin permissions)

-internally manage schedule:

-pull schedule data from spreadsheet

    -keep internal tracker (or separate spreadsheet?) for which week of the season it is and the matches for that week
    
    -could have a command to display the schedule for that week
    
    -update after match results are posted
    
    -once all matches for the week are complete, run the kill leaders script (could cause issues if a match gets 
    an extension but another match for the next week happens before the extension match, would just mean the k/d info
    would be slightly off as it would be either missing a match or have an extra match)

-pokedex data, showdown command type stuff (which API has this info?):
    
    -ideally would be able to have commands similar to ones in showdown
    
    -weak, effectiveness, coverage, learn, dex, data, dexsearch, details
    
    -https://pokemondb.net/pokebase/252493/what-are-all-the-commands-in-pokemon-showdown

-keep database of all replays, with the season and two coaches that battled

-track statistics across seasons for each coach (win/loss rate, h2h with other coaches, etc)

-use head2head as a tiebreaker when updating standings


# Resources:
https://realpython.com/how-to-make-a-discord-bot-python/
https://github.com/Rapptz/discord.py/tree/v1.7.3/examples
https://discordpy.readthedocs.io/en/stable/index.html
https://discordpy.readthedocs.io/en/stable/faq.html
