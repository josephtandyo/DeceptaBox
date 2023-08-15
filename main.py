import asyncio
import discord
import os
from discord.ext import commands

import settings
import tokens
from cogs.DeathHandling import DeathHandling
from cogs.PlayerData import PlayerData
from cogs.WrongChat import WrongChat

# file location is changeable in settings.py
os.chdir(settings.file_location)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

# to be able to call methods inside the cogs
#TODO crtl f every cog class to see if the commands are crrect and parametere, THERE IS NO ERROR CHECKING FOR THESE
client.player_data = PlayerData(client)
client.wrong_chat = WrongChat(client)
client.death_handling = DeathHandling(client)

# TODO checks to see if their settings have send DM enabled. If not, send a message you need it enabled, send message to guest that player doesnt have it enabled
# in the add_player method, check
# TODO some of the embeds say "author" but change this to author.name
#TODO rename some vairable names... some of these are atrocius
@client.event
async def on_ready():
    print("Ready")
    # TODO await client.player_data.reset()


# loading all the cogs
async def load():
    # for every file in the cogs folder
    for filename in os.listdir("./cogs"):
        # if it is a py file
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
            print(f"cogs.{filename[:-3]} is loaded")


# starting the bot
async def main():
    async with client:
        # load the cogs
        await load()
        # start the bot client
        await client.start(tokens.key)  # this token is kept secret


asyncio.run(main())
