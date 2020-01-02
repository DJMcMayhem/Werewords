import discord
from discord.ext import tasks

from emoji import Emoji
import time
import sys
import bot

client = discord.Client()

dude = bot.Bot(client)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await dude.handle_message(message)
    return

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    await dude.handle_reaction_add(reaction, user)

@tasks.loop(seconds=1)
async def bot_loop():
    await dude.bot_loop()

with open("token.txt") as f:
    token = f.read().strip()

bot_loop.start()
client.run(token)
