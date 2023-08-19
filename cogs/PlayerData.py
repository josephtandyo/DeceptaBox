from discord.ext import commands
import discord
import SendEmbed


# STATUS: FINISHED
# class for player data for error messages regarding the use of commands
class PlayerData(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("PlayerData Cog is ready")

    # this error is for when a player tries to visit another player when the visiting timer has not finished
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        channel = ctx.channel

        if isinstance(error, commands.CommandOnCooldown):
            await SendEmbed.send_visit_time_error(channel, error)

    # this error is for when a user has their privacy settings disabled, not allowing the bot to DM them
    async def cant_dm_user(self, user: discord.User):

        # if there's no user or the user is the bot return
        if user is None or user == self.client.user:
            return

        # try sending message
        try:
            await user.send()

        # return true when they can't be DMd
        except discord.Forbidden:
            return True
        # return false when they can be DMd
        except discord.HTTPException:
            return False


async def setup(client):
    await client.add_cog(PlayerData(client))
