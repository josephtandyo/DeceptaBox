from discord.ext import commands
import discord


class PlayerData(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("PlayerData Cog is ready")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em_tired = discord.Embed(color=discord.Color.yellow())
            minutes = int(error.retry_after / 60)
            rounded = (error.retry_after / 60) - minutes
            seconds = int(rounded * 60)
            em_tired.add_field(name=f"You can't visit anyone for **{minutes} minutes** and **{seconds} seconds**",
                               value="This is because you are tired after the last visit")
            em_tired.set_footer(text="To check how much time until the next visit, visit the bot in the DM")
            await ctx.channel.send(embed=em_tired)

    async def cant_dm_user(self, user: discord.User):
        if user is None or user == self.client.user:
            return
        try:
            await user.send()
        except discord.Forbidden:
            return True
        except discord.HTTPException:
            return False


async def setup(client):
    await client.add_cog(PlayerData(client))
