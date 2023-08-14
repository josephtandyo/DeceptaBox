import discord
from discord.ext import commands


class Test(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("test is ready")
        await self.testing()  # Call the testing method when the bot is ready

    async def testing(self):
        user = await self.client.fetch_user(296100775795621888)
        print("hello " + user.name)


async def setup(client):
    await client.add_cog(Test(client))
