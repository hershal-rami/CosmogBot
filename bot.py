import asyncio
import logging
import os

import discord
from discord.ext import commands

from standings import updateMatchResults, getFormattedStandings

# Basic logging info outputs to discord.log file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Discord token set locally for security
TOKEN = os.getenv('DISCORD_TOKEN')

activity = discord.Activity(type=discord.ActivityType.listening, name="it's trainer! | .help")
bot = commands.Bot(command_prefix='.', activity=activity)

# Runs once logged in and ready for additional actions
@bot.event
async def on_ready():
    print('A wild {0.user} appeared!'.format(bot))

# Overriding on_message stops commands from running, use a listener instead
@bot.listen('on_message')
async def responder(message):
    if "Result:" in message.content:
        await message.channel.send("Working on it!")
        updateMatchResults(message.content)
        await message.channel.send("Standings have been updated!!")

    # Need this to prevent bot from responding to itself infinitely
    if message.author == bot.user:
        return
    
    # Fun responses: emoji responses, reactions, and hello message
    if ":scepthink:" in message.content.lower():
        await message.channel.send("<:scepthink:932156902555648101>") # must use emoji id
    elif ":thonk:" in message.content.lower():
        await message.channel.send("<:thonk:932152527061913640>")
    elif ":copium:" in message.content.lower():
        await message.channel.send("<:copium:932152187616895006>")
    elif ":cosmug:" in message.content.lower():
        await message.channel.send("<:cosmug:932895668450787329>")
    elif "cosmog" in message.content.lower():
        await message.add_reaction("<:cosmug:932895668450787329>")
    elif message.content.lower().startswith(('hello', 'hi', 'hey')):
        await message.channel.send('Pepew! *(Hello!)*')


@bot.command(name='splash', help='Cosmog\'s best attack!')
async def use_splash(ctx):
    await ctx.send("Cosmog used splash!")
    await asyncio.sleep(1) # dont use time.sleep, causes blocking
    await ctx.send("But nothing happened!")


@bot.command(name='standings', help='Gets the current league standings')
async def print_standings(ctx):
    await ctx.send('```' + getFormattedStandings() + '```')

# Go, Cosmog!
bot.run(TOKEN)