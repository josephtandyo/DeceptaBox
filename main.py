import asyncio
import discord
import os
from discord.ext import commands

import settings
import tokens
from cogs.PlayerData import PlayerData

# file location is changeable in settings.py
os.chdir(settings.file_location)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

# to be able to call methods inside the PlayerData.py cog
client.player_data = PlayerData(client)


@client.event
async def on_ready():
    print("Ready")
    await client.player_data.reset()


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
            print(f"cogs.{filename[:-3]} is loaded")


async def main():
    async with client:
        await load()
        await client.start(tokens.key)


asyncio.run(main())
