import discord
from discord.ext import commands
import GetSetStats
import SendEmbed
import settings


# STATUS: FINISHED
# cog class for visiting commands (part of guest commands)
class VisitingCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("VisitingCommands Cog is ready")

    # !visit @player is a command to allow guests to visit @player
    # there is a cooldown for this command, as users can visit players every 5 minutes (300 seconds)
    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, settings.cooldown_time, commands.BucketType.user)
    async def visit(self, ctx, player: discord.Member):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # check to see if author and player can be DMd
        if await self.client.player_data.cant_dm_user(author):
            await SendEmbed.send_cant_dm_author(channel)
            return

        if await self.client.player_data.cant_dm_user(player):
            await SendEmbed.send_cant_dm_player(player, channel)
            return

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(author, channel.id, server):
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author visiting the bot itself
        if player == self.client.user:
            await SendEmbed.send_bot_visit(author)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # add the author and player to players.json
        await self.client.leaderboards_handling.add_player(author)
        await self.client.leaderboards_handling.add_player(player)

        # check if the player being visited has been visited by this author already
        visited_list = await GetSetStats.get_stat(author.id, "List Of Visitors")
        for visited_players_id in visited_list:
            if visited_players_id == player.id:
                await SendEmbed.send_visited_already(author, player, channel)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

        # check if author is dead and trying to visit
        # if the results are true then author is dead and return and reset cooldown
        if await GetSetStats.get_stat(author.id, "Dead"):
            self.client.get_command("visit").reset_cooldown(ctx)
            await SendEmbed.send_author_d(author, channel)
            return
        # check if player is dead and trying to get visited
        if await GetSetStats.get_stat(player.id, "Dead"):
            self.client.get_command("visit").reset_cooldown(ctx)
            await SendEmbed.send_player_d(player, channel)
            return

        # author visiting themselves
        if player == author:
            await SendEmbed.send_visit_self(author, channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author visiting no one
        elif player is None:
            await SendEmbed.send_visit_no_one(author, channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # check if author is already visiting
        already_visiting = await GetSetStats.get_stat(author.id, "Visiting")
        # check if there's a guest in player's home
        guest_at_players = await GetSetStats.get_stat(player.id, "Visited")
        # check if there's a player in author's home
        guest_at_authors = await GetSetStats.get_stat(author.id, "Visited")
        # check if the player is visiting a different host
        player_not_home = await GetSetStats.get_stat(player.id, "Visiting")
        # check if there's a gift in author's inventory
        inventory_full = await GetSetStats.get_stat(author.id, "Received")

        # author is already at a player's house trying to visit again
        if already_visiting:

            # check who the player is that author is currently visiting
            player_visited = await self.client.fetch_user(already_visiting)

            # if author is currently visiting someone else other than the player
            if player != player_visited:
                await SendEmbed.send_v_someone_else(author, player, channel, player_visited)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

            # if author is already visiting the player
            elif player == player_visited:
                await SendEmbed.send_v_already(author, player, channel)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

        # author is trying to visit a player that is being visited by someone else
        elif guest_at_players:
            guest_inside_players = await self.client.fetch_user(guest_at_players)
            await SendEmbed.send_guest_at_host(author, player, channel, guest_inside_players)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is trying to visit a player, but didn't send their own visitor a gift yet
        elif guest_at_authors:
            guest_inside_authors = await self.client.fetch_user(guest_at_authors)
            await SendEmbed.send_guest_at_home(author, player, channel, guest_inside_authors)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is trying to visit a player that is not home and visiting someone else
        elif player_not_home:
            player_visiting = await self.client.fetch_user(player_not_home)
            await SendEmbed.send_not_home(author, player, channel, player_visiting)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is trying to visit a player, but hasn't opened their previous gift
        elif inventory_full:
            await SendEmbed.send_full_inventory(author, player, channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is visiting a valid player
        else:
            # update the stats and send the message
            await GetSetStats.update_successful_visit_stats(author.id, player.id)
            await SendEmbed.send_visiting_player(author, player, channel)

    # !home is for the author to go back home, after visiting a player (if the player takes too long sending gift)
    @commands.command()
    async def home(self, ctx):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return
        if await self.client.wrong_chat.check_guest_wc(author, channel.id, server):
            return

        # check if author is dead and trying to go home
        # if the results are true then author is dead and return
        if await GetSetStats.get_stat(author.id, "Dead"):
            await SendEmbed.send_author_d(author, channel)
            return

        # add author to the players.json file
        await self.client.leaderboards_handling.add_player(author)
        # check if visiting player
        visiting_player_id = await GetSetStats.get_stat(author.id, "Visiting")
        # check if received gift
        received_gift = await GetSetStats.get_stat(author.id, "Received")

        # author is not visiting any player (they are already at home)
        if not visiting_player_id:
            await SendEmbed.send_home_already(author, channel)
            return

        # author tries to go home, but has already received gift
        elif received_gift:
            await SendEmbed.send_received_already(author, channel)
            return

        # author successfully leaves home
        else:
            player = await self.client.fetch_user(visiting_player_id)
            # set the new stats
            await GetSetStats.update_successful_home_stats(author.id, player.id)
            # send message
            await SendEmbed.send_go_home(author, player, channel)

            # reset cooldown because cancelled visit
            self.client.get_command("visit").reset_cooldown(ctx)


# cog setup
async def setup(client):
    await client.add_cog(VisitingCommands(client))
