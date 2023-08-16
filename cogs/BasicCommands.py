import discord
from discord.ext import commands

import GetSetStats
import LeaderboardsHandling
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
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong channel and return
        if await self.client.wrong_chat.check_basic_wc(author, channel.id, server):
            return

        # send the rules
        await SendEmbed.send_rules(channel)

    # !guide is a command that will send the list of commands for the game
    @commands.command()
    async def guide(self, ctx):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(author, channel.id, server):
            return

        # send the guide
        await SendEmbed.send_guide(channel)

    # !stats is a command that will send stats of author
    # !stats @player will send the stats for @player
    @commands.command()
    async def stats(self, ctx, player: discord.Member = None):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild
        send_here = ctx.send

        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(author, channel.id, server):
            return

        # author checking stats of the bot itself
        if player == self.client.user:
            await SendEmbed.send_bot_stats(author, send_here)
            return

        # author checking their own stats (when there is no @ referenced or the @ is the author)
        elif player is None or player == author:

            # add the author to players.json
            await self.client.player_data.add_player(author)
            user = author

        # author checking other player's stats
        else:

            # add the player to players.json
            await self.client.player_data.add_player(player)
            user = player

        # get each stat for user
        total_points = await GetSetStats.get_stat(user.id, "Total Points")
        trashability_amt = await GetSetStats.get_stat(user.id, "Trashability")

        opened_gift_points = await GetSetStats.get_stat(user.id, "Unboxed Points")
        killing_host_points = await GetSetStats.get_stat(user.id, "Accidental Kill")

        returned_gift_points = await GetSetStats.get_stat(user.id, "Declined Points")
        killing_guest_points = await GetSetStats.get_stat(user.id, "Kill Points")

        # send the stats
        await SendEmbed.send_stats(user, total_points, trashability_amt, opened_gift_points,
                                   killing_host_points, returned_gift_points, killing_guest_points,
                                   author, send_here)

    # !leaderboards will send the leaderboards
    @commands.command()
    async def leaderboards(self, ctx):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(author, channel.id, server):
            return

        lb_name_id_list, lb_points_list, lb_death_bool_list = await LeaderboardsHandling.get_sorted_valid_stats()
        lb_name_list = []
        for user_id in lb_name_id_list:
            bal = await self.client.fetch_user(user_id)

            lb_name_list.append(bal.name)

        lb_death_list = []
        for boolean in lb_death_bool_list:
            if boolean:
                lb_death_list.append("Alive")
            else:
                lb_death_list.append("Dead")

        # send the leaderboards
        await SendEmbed.send_leaderboards(lb_name_list, lb_points_list, lb_death_list, channel)

    @commands.command()
    async def highscores(self, ctx):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # check if the command is sent in wrong chat
        # return if sent in wrong channel
        if await self.client.wrong_chat.check_basic_wc(author, channel.id, server):
            return

        # get the list of players, the list of scores, the list of deaths
        name_list, value_list, death_list = await self.client.player_data.make_highscores()

        # send the highscores
        await SendEmbed.send_highscores(name_list, value_list, death_list, channel)


# cog setup
async def setup(client):
    await client.add_cog(BasicCommands(client))
