import discord
from discord.ext import commands
import DataHelper
import SendEmbed


# cog class for basic commands
class BasicCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_start(self):
        print("BasicCommands Cog is ready")

    # !rules is a command that will send rules of the game
    @commands.command()
    async def rules(self, ctx):

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong channel and return
        if await self.client.wrong_chat.check_basic_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # send the rules
        await SendEmbed.send_rules(ctx.channel)

    # !guide is a command that will send the list of commands for the game
    @commands.command()
    async def guide(self, ctx):

        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # send the guide
        await SendEmbed.send_guide(ctx.channel)

    # !stats is a command that will send stats of author
    # !stats @player will send the stats for @player
    @commands.command()
    async def stats(self, ctx, member: discord.Member = None):

        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # author checking stats of the bot itself
        if member == self.client.user:
            await SendEmbed.send_bot_stats(ctx.author, ctx.send)
            return

        # author checking their own stats (when there is no @ referenced or the @ is the author)
        elif member is None or member == ctx.author:

            # add the author to players.json
            await self.client.player_data.add_player(ctx.author)
            user = ctx.author

        # author checking other player's stats
        else:

            # add the player to players.json
            await self.client.player_data.add_player(member)
            user = member

        # get the list in players.json file
        users = await DataHelper.get_player_data()

        # get the information of the user that is being looked up from players.json
        total = users[str(user.id)]["Total Points"]
        trashability = users[str(user.id)]["Trashability"]
        nice_amt = users[str(user.id)]["Unboxed Points"]
        decline_amt = users[str(user.id)]["Declined Points"]
        kills_amt = users[str(user.id)]["Kill Points"]
        accident_amt = users[str(user.id)]["Accidental Kill"]

        # send the stats
        await SendEmbed.send_stats(user, total, trashability, nice_amt, accident_amt, decline_amt, kills_amt,
                                   ctx.author, ctx.send)

    @commands.command()
    async def leaderboards(self, ctx):

        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # get the leaderboard title, the list of players, the list of scores, the list of death status
        title, name_list, value_list, status = await self.client.player_data.make_leaderboard()

        # send the leaderboards
        await SendEmbed.send_leaderboards(title, name_list, value_list, status, ctx.channel)

    @commands.command()
    async def highscores(self, ctx):
        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # get the list of players, the list of scores, the list of deaths
        name_list, value_list, death_list = await self.client.player_data.make_highscores()

        # send the highscores
        await SendEmbed.send_highscores(name_list, value_list, death_list, ctx.channel)


# cog setup
async def setup(client):
    await client.add_cog(BasicCommands(client))
