import asyncio
import logging
import os
import random
from datetime import datetime

import discord
from discord.ext import tasks, commands

import replay_analyze
import database
from commands import Moveset, Spreadsheets, TeamManagement

# Basic logging info outputs to discord.log file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Discord token set locally for security
TOKEN = os.getenv('DISCORD_TOKEN')
GM = False

# Need members intent for managing member stuff
intents = discord.Intents.default()
intents.members = True

activity = discord.Activity(type=discord.ActivityType.listening, name="its trainer! | .help")
bot = commands.Bot(command_prefix='.', activity=activity, intents=intents)

# Runs once logged in and ready for additional actions
@bot.event
async def on_ready():
    print('A wild {0.user} appeared!'.format(bot))

# Resets GM variable every 12 hours
@tasks.loop(hours=12)
async def reset_gm(self):
    global GM
    GM = False

# Overriding on_message stops commands from running, use a listener instead
@bot.listen('on_message')
async def responder(message):
    global GM

    # Need this to prevent bot from responding to itself infinitely
    if message.author == bot.user:
        return        

    # Updating standings after Porygon posts match results
    # if "Result:" in message.content:
    #     await message.channel.send("Working on it!")
    #     await message.channel.send(updateMatchResults(message.content))

    # Fun responses: emoji responses, reactions, and hello message
    if ":scepthink:" in message.content.lower():
        await message.channel.send("<:scepthink:932156902555648101>") # must use emoji id    
    if ":thonk:" in message.content.lower():
        await message.channel.send("<:thonk:932152527061913640>")
    if ":copium:" in message.content.lower():
        await message.channel.send("<:copium:932152187616895006>")
    if "sdn" in message.content.lower():
        await message.channel.send("<:sdn:932156913012047922>")
    if ":cosmug:" in message.content.lower():
        await message.channel.send("<:cosmug:932895668450787329>")
    if "cosmog" in message.content.lower():
        await message.add_reaction("<:cosmug:932895668450787329>")

    if "!cosmogdb" in message.content.lower():
        print("testing")
        await message.channel.send("testing")
        msg = ""
        try:
            msg = database.user_input(message.content)
            await message.channel.send(msg)
        except:
            await message.channel.send("Something went wrong")

    # Only say hi in the general channel
    if message.channel.name == "general":
        if any(x in message.content.lower().split(" ") for x in ('hello', 'hi', 'hey', 'hiya')):
            await message.channel.send(random.choice(['Pepew! *(Hello!)*', 'Pepew! *(Hi!)*', 'Pepew! *(Heya!)*']))

    # only respond if gm is sent before 2pm
    if not GM and any(x in message.content.lower() for x in ('gm', 'mornin')):
        GM = True
        await message.channel.send("Pe-pepew! *(Good morning!)*")
        await message.channel.send(file=discord.File('content/gm.gif'))

    # look out for replays and send a message that is the K/D result of that game
    if "replay.pokemonshowdown.com" in message.content.lower():
        try:
             await message.channel.send(replay_analyze.get_match_result(message.content))
        except:
             await message.channel.send("Uh Oh")

async def main():
    async with bot:
        await bot.add_cog(Moveset(bot))
        await bot.add_cog(Spreadsheets(bot))
        await bot.add_cog(TeamManagement(bot))
        await bot.start(TOKEN)

# Go, Cosmog!
asyncio.run(main())