import asyncio
import logging
import random
import os
from datetime import datetime

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

    if ":thonk:" in message.content.lower():
        await message.channel.send("<:thonk:932152527061913640>")

    if ":copium:" in message.content.lower():
        await message.channel.send("<:copium:932152187616895006>")

    if ":sdn:" in message.content.lower():
        await message.channel.send("<:sdn:932156913012047922>")

    if ":cosmug:" in message.content.lower():
        await message.channel.send("<:cosmug:932895668450787329>")

    if "cosmog" in message.content.lower():
        await message.add_reaction("<:cosmug:932895668450787329>")

    if any(x in message.content.lower().split(" ") for x in ('hello', 'hi', 'hey', 'hiya')):
        await message.channel.send(random.choice(['Pepew! *(Hello!)*', 'Pepew! *(Hi!)*', 'Pepew! *(Heya!)*']))

    # only respond if gm is sent before 2pm
    if datetime.now().hour <= 14 and any(x in message.content.lower() for x in ('gm', 'mornin')):
        await message.channel.send("Pe-pepew! *(Good morning!)*")
        await message.channel.send(file=discord.File('gm.gif'))


@bot.command(name='splash', help='Cosmog\'s best attack!')
async def use_splash(ctx):
    await ctx.send("Cosmog used splash!")
    await asyncio.sleep(1) # dont use time.sleep, causes blocking
    await ctx.send("But nothing happened!")


@bot.command(name='teleport', help='Cosmog\'s second best attack!')
async def use_teleport(ctx):
    await ctx.send("Cosmog used teleport!")
    await ctx.send(file=discord.File('teleport.gif'))
    await asyncio.sleep(2)
    await ctx.send("Cosmog fled from battle!")


@bot.command(name='doc', help='Gets the current league spreadsheet for each division')
async def print_doc(ctx):
    await ctx.send('Solgaleo Division:\n<https://docs.google.com/spreadsheets/d/1LYqMD8aLMLdkVL1bDrmk5QYRoaFCr0zdJq4JQvIc6TA/edit#gid=253592106>\nLunala Division:\n<https://docs.google.com/spreadsheets/d/1L7_Vr7LMjmIC-zMY6YPTc31wVhjG_a1CkmzVONrvXdM/edit#gid=253592106>')


@bot.command(name='standings', help='Gets the current league standings')
async def print_standings(ctx):
    await ctx.send('```' + getFormattedStandings() + '```')


@bot.command(name='createteam', help='Usage: .createteam @User, Hex, Team Name')
@commands.has_permissions(manage_roles=True)
async def createteam(ctx, *, message):
    # TODO if not mod then throw error
    # insufficient role/perms

    # split message into individual arguments and format
    args = message.split(',')

    if len(args) < 3:
        #TODO fix error handling
        await ctx.send("error msg")
        raise commands.MissingRequiredArgument

    # TODO error handling on incorrect format (no commas)

    user_id = args[0].strip()
    hex_code = args[1].strip()

    # remove only leading space
    team_name = args[2]
    if team_name[0] == ' ':
        team_name = team_name[1::]
    
    duplicate = discord.utils.get(ctx.message.guild.roles, name=team_name)
    if duplicate is not None:
        # TODO throw error if role already exists
        print("error team name already exists")

    # TODO fix color of role
    perms=discord.Permissions(administrator=True)
    await ctx.message.guild.create_role(name=team_name, permissions=perms)
    
    # TODO remove No Team role from user using id
    # TODO add newly created role to user using id

    # TODO await ctx.send('Team $teamname has been created for Coach {user}!')

    await ctx.send('role made')


@createteam.error
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Incorrect/missing arguments. Format should be '.createteam @User, Hex, Team Name") 

# Go, Cosmog!
bot.run(TOKEN)