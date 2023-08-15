import discord
from discord.ext import commands

import DataHelper
import SendEmbed


# cog class for visiting commands (part of guest commands)
class VisitingCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("VisitingCommands is ready")

    # !visit @player is a command to allow guests to visit @player
    # there is a cooldown for this command, as users can visit players every 5 minutes (300 seconds)
    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def visit(self, ctx, member: discord.Member):

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(ctx.channel.id, ctx.guild, ctx.author):
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author visiting the bot itself
        if member == self.client.user:
            await SendEmbed.send_bot_visit(ctx.author)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # add the author and player to players.json
        await self.client.player_data.add_player(ctx.author)
        await self.client.player_data.add_player(member)

        # check if author or player is dead and trying to visit or get visited
        # if the results are true then author is dead or player visited is dead and return and reset cooldown
        if await self.client.death_handling.check_death(ctx.channel, ctx.author, member):
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author visiting themselves
        if member == ctx.author:
            await SendEmbed.send_visit_self(ctx.author, ctx.channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author visiting no one
        elif member is None:
            await SendEmbed.send_visit_no_one(ctx.author, ctx.channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # get the data of the list of players
        users = await DataHelper.get_player_data()

        # check inventory, already visiting, someone at home for the author
        inventory_full = users[str(ctx.author.id)]["Received"]
        already_visiting = users[str(ctx.author.id)]["Visiting"]
        guest_at_home = users[str(ctx.author.id)]["Visited"]

        # check guest at player's, player not home for the player
        guest_at_host = users[str(member.id)]["Visited"]
        not_home = users[str(member.id)]["Visiting"]

        # author is already at someone's house trying to visit again
        if already_visiting:

            # check who it is that author is currently visiting
            user_visiting = await self.client.fetch_user(already_visiting)

            # if author is currently visiting someone else other than the player
            if member != user_visiting:
                await SendEmbed.send_v_someone_else(user_visiting, member, ctx.author, ctx.channel)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

            # if author is already visiting the player
            elif member == user_visiting:
                await SendEmbed.send_v_already(member, ctx.author, ctx.channel)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

        # author is trying to visit a player that is being visited by someone else
        elif guest_at_host:
            guest_inside = await self.client.fetch_user(guest_at_host)
            await SendEmbed.send_guest_at_host(member, guest_inside, ctx.author, ctx.channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is trying to visit a player, but didn't send their own visitor a gift yet
        elif guest_at_home:
            guest_inside = await self.client.fetch_user(guest_at_home)
            await SendEmbed.send_guest_at_home(member, guest_inside, ctx.author, ctx.channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is trying to visit a player that is visiting someone else
        elif not_home:
            host_elsewhere = await self.client.fetch_user(not_home)
            await SendEmbed.send_not_home(member, host_elsewhere, ctx.author, ctx.channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is trying to visit a player, but hasn't opened their previous gift
        elif inventory_full:
            await SendEmbed.send_full_inventory(member, ctx.author, ctx.channel)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # author is visiting a valid player
        else:
            await DataHelper.update_stats(member.id, 0, ctx.author.id, "Visited")
            await DataHelper.update_stats(ctx.author.id, 0, member.id, "Visiting")
            await SendEmbed.send_visiting_player(member, ctx.author, ctx.channel)

    # !home is for the author to go back home, after visiting a player (if the player takes too long sending gift)
    @commands.command()
    async def home(self, ctx):

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return
        if await self.client.wrong_chat.check_guest_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # check if author is dead and trying to go home
        # if the results are true then author is dead and return
        # (yes pass in author twice, but it doesn't ever matter)
        if await self.client.death_handling.check_death(ctx.channel, ctx.author, ctx.author):
            return

        # add author to the players.json file
        await self.client.player_data.add_player(ctx.author)

        # get the players.json file
        users = await DataHelper.get_player_data()

        # check if gift received and if visiting player
        received_gift = users[str(ctx.author.id)]["Received"]
        visiting_player = users[str(ctx.author.id)]["Visiting"]

        # author is not visiting any player (they are already at home)
        if not visiting_player:
            await SendEmbed.send_home_already(ctx.author, ctx.channel)
            return

        # author tries to go home, but has already received gift
        elif received_gift:
            await SendEmbed.send_received_already(ctx.author, ctx.channel)
            return

        # author successfully leaves home
        else:
            for player_id in users.keys():
                # find the player who author was visiting
                if int(player_id) == int(users[str(ctx.author.id)]["Visiting"]):
                    # put player in players.json file if not yet on it
                    member_obj = await self.client.player_data.make_member(int(player_id))

                    # update stats of player and author
                    await DataHelper.update_stats(ctx.author.id, 0, False, "Visiting")
                    await DataHelper.update_stats(member_obj.id, 0, False, "Visited")

                    await SendEmbed.send_go_home(member_obj, ctx.author, ctx.channel)

                    # reset cooldown because cancelled visit
                    self.client.get_command("visit").reset_cooldown(ctx)


# cog setup
async def setup(client):
    await client.add_cog(VisitingCommands(client))
