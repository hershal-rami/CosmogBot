import logging
import os

import discord

# Basic logging info outputs to discord.log file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Discord token set locally for security
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if ":scepthink:" in message.content.lower():
        await message.channel.send(":scepthink:")
    
    if ":thonk:" in message.content.lower():
        await message.channel.send(":thonk:")

    if message.content.lower.startswith('hello'):
        await message.channel.send('Hello!')

client.run(TOKEN)