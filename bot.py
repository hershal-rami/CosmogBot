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
    # if "Result:" in message.content:
    #     await message.channel.send("Working on it!")
    #     updateMatchResults(message.content)
    #     await message.channel.send("Standings have been updated!!")

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
    elif ":sdn:" in message.content.lower():
        await message.channel.send("<:sdn:932156913012047922>")
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


@bot.command(name='doc', help='Gets the current league spreadsheet')
async def print_doc(ctx):
    await ctx.send('<https://docs.google.com/spreadsheets/d/1LYqMD8aLMLdkVL1bDrmk5QYRoaFCr0zdJq4JQvIc6TA/edit?usp=sharing>')


@bot.command(name='standings', help='Gets the current league standings')
async def print_standings(ctx):
    await ctx.send('```' + getFormattedStandings() + '```')


@bot.command(name='createteam', help='.createteam @User, Hex, Team Name')
async def createteam(ctx, *, message):
    # split message into individual arguments and format
    args = message.split(',')

    if len(args) != 3:
        await ctx.send("error msg")
        raise commands.MissingRequiredArgument

    user_id = args[0].strip()
    
    hex_code = args[1]
    if hex_code[0] == ' ':
        hex_code = hex_code[1::]

    team_name = args[2]
    if team_name[0] == ' ':
        team_name = team_name[1::]

    print(message)
    print(args)
    print(user_id)
    print(hex_code)
    print(team_name)

@createteam.error
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Incorrect/missing arguments. Format should be '.createteam @User, Hex, Team Name") 

# Go, Cosmog!
bot.run(TOKEN)