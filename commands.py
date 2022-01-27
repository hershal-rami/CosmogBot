import asyncio

import discord
from discord.ext import commands

from standings import getFormattedStandings, updateMatchResults

class Moveset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='splash', help='Cosmog\'s best attack!')
    async def splash(self, ctx):
        await ctx.send("Cosmog used splash!")
        await asyncio.sleep(1) # dont use time.sleep, causes blocking
        await ctx.send("But nothing happened!")

    @commands.command(name='teleport', help='Cosmog\'s second best attack!')
    async def teleport(self, ctx):
        await ctx.send("Cosmog used teleport!")
        await ctx.send(file=discord.File('teleport.gif'))
        await asyncio.sleep(2)
        await ctx.send("Cosmog fled from battle!")


class Spreadsheets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='doc', help='Gets the current league spreadsheet for both divisions')
    async def doc(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('test')
            await ctx.send('Solgaleo Division:\n<https://docs.google.com/spreadsheets/d/1LYqMD8aLMLdkVL1bDrmk5QYRoaFCr0zdJq4JQvIc6TA/edit#gid=253592106>\nLunala Division:\n<https://docs.google.com/spreadsheets/d/1L7_Vr7LMjmIC-zMY6YPTc31wVhjG_a1CkmzVONrvXdM/edit#gid=253592106>')

    @doc.command(name='doc solgaleo', help='Gets the Solgaleo division spreadsheet',)
    async def doc_solgaleo(self, ctx):
        await ctx.send('Solgaleo Division:\n<https://docs.google.com/spreadsheets/d/1LYqMD8aLMLdkVL1bDrmk5QYRoaFCr0zdJq4JQvIc6TA/edit#gid=253592106>')

    @doc.command(name='doc lunala', help='Gets the Lunala division spreadsheet')
    async def doc_lunala(self, ctx):
        await ctx.send('Lunala Division:\n<https://docs.google.com/spreadsheets/d/1L7_Vr7LMjmIC-zMY6YPTc31wVhjG_a1CkmzVONrvXdM/edit#gid=253592106>')

    @commands.command(name='standings', help='Gets the current league standings')
    async def standings(self, ctx):
        await ctx.send('```' + getFormattedStandings() + '```')


class TeamManagement(commands.Cog, name='Team Management'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='support', help='Gives a user with no team the team role for the provided team')
    async def support(self, ctx, *, args):
        # Check for illegal roles
        team_name = args
        if team_name in ['MBTL Bronze Medalist', 'MBTL Silver Medalist', 'MBTL Gold Medalist', 'Bot']:
            # TODO error if team is a medalist role
            print("error this is a medalist role")
            return

        # Check that team role exists
        guild = ctx.message.guild
        team_role = discord.utils.get(guild.roles, name=team_name)
        if team_role is None:
            # TODO error if team does not exist
            print("this team does not exist")
            return

        # Remove No Team role
        no_team = discord.utils.get(guild.roles, name='No Team')
        member = ctx.message.author
        await member.remove_roles(no_team)

        # Add team role
        await member.add_roles(team_role)
        await ctx.send(member.name + " is now supporting " + team_name + "!")

    @commands.command(name='unsupport', help='Removes a team role from a user, wow harsh...')
    async def unsupport(self, ctx, *, args):
        # Check for illegal roles
        team_name = args
        if team_name in ['MBTL Bronze Medalist', 'MBTL Silver Medalist', 'MBTL Gold Medalist', 'Bot']:
            # TODO error if team is a medalist role
            print("error this is a medalist role")
            return

        # Check that team role exists
        guild = ctx.message.guild
        team_role = discord.utils.get(guild.roles, name=team_name)
        if team_role is None:
            # TODO error if team does not exist
            print("this team does not exist")
            return

        # Remove team role
        member = ctx.message.author
        await member.remove_roles(team_role)

        # Add No Team role
        no_team = discord.utils.get(guild.roles, name='No Team')
        await member.add_roles(no_team)
        await ctx.send(member.name + " is no longer supporting " + team_name + "...")

    @commands.command(name='createteam', help='Usage: .createteam @User, Hex, Team Name')
    async def createteam(self, ctx, *, message):
        # TODO if not mod then throw error
        # insufficient role/perms

        # split message into individual arguments and format
        args = message.split(',')

        if len(args) < 3:
            #TODO fix error handling
            await ctx.send("error msg")
            raise commands.MissingRequiredArgument

        # TODO error handling on incorrect format (no commas)

        user_id = int(args[0].strip()[3:-1])
        hex_code = int(args[1].strip(), 16)
        
        # remove only leading space
        team_name = args[2]
        if team_name[0] == ' ':
            team_name = team_name[1:]

        guild = ctx.message.guild
        duplicate = discord.utils.get(guild.roles, name=team_name)
        if duplicate is not None:
            # TODO throw error if role already exists
            print("error team name already exists")
        
        # Create role with specified name and color
        perms=discord.Permissions(administrator=True)
        await guild.create_role(name=team_name, color=discord.Color(hex_code), permissions=perms)

        # Remove No Team role from user using id
        no_team = discord.utils.get(guild.roles, name='No Team')
        member = guild.get_member(user_id)
        await member.remove_roles(no_team)
        
        # Add newly created role to user using id
        team_role = discord.utils.get(guild.roles, name=team_name)
        await member.add_roles(team_role)
        
        output = "Team " + team_name + " has been created for Coach " + member.name +"!"
        await ctx.send(output)

    @createteam.error
    async def on_command_error(error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Incorrect/missing arguments. Format should be '.createteam @User, Hex, Team Name") 