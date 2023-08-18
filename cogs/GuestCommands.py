from discord.ext import commands
from discord.utils import get
import GetSetHighscores
import GetSetStats
import SendEmbed
import settings


# cog class for guest commands (unbox, decline and trashing)
class GuestCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("GuestCommands Cog is ready")

    # !unbox is a command that opens the gift given by the host
    @commands.command()
    async def unbox(self, ctx):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # get the type of gift unboxed and get the giver id
        gift_type = await GetSetStats.get_stat(author.id, "Received")
        giver_id = await GetSetStats.get_stat(author.id, "Giver")

        # get the giver
        giver = await self.client.fetch_user(giver_id)

        # check to see if author and player can be DMs
        if await self.client.player_data.cant_dm_user(author):
            await SendEmbed.send_cant_dm_author(channel)

        if await self.client.player_data.cant_dm_user(giver):
            await SendEmbed.send_cant_dm_player(giver, channel)

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(author, channel.id, server):
            return

        # check if author is dead and trying to unbox
        # if the results are true then author is dead and return
        if await GetSetStats.get_stat(author.id, "Dead"):
            await SendEmbed.send_author_d(author, channel)
            return

        # add author to the players.json if not yet added
        await self.client.player_data.add_player(author)

        # if there is no gift to unbox
        if gift_type is False:
            await SendEmbed.send_udt_nothing(author, channel)

        # if the gift unboxed was a nice gift
        elif gift_type == "nice" and giver_id is not False:

            # update the stats for unboxing nice gifts
            await GetSetStats.update_unbox_nice_stats(author.id, giver_id)
            # send the message
            await SendEmbed.send_unbox_nice(author, channel)
            # add author to highscore json
            await self.client.highscore_handling.add_highscore(author)
            # update highscore of the author
            await GetSetHighscores.update_highscore(author.id)

            return

        elif gift_type == "devious" and giver_id is not False:

            # update the stats for unboxing devious gifts
            await GetSetStats.update_unbox_devious_stats(author.id, giver_id)
            # send the message
            await SendEmbed.send_unbox_devious(ctx.author, ctx.channel, giver)

            # give the author the dead role for unboxing devious gift
            dead_role = get(server.roles, name=settings.dead_role_NAME)
            await author.add_roles(dead_role)

            # add giver to json
            await self.client.highscore_handling.add_highscore(giver)
            await GetSetHighscores.update_highscore(giver.id)

    @commands.command()
    async def decline(self, ctx):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild
        # get the type of gift unboxed and get the giver id
        gift_type = await self.client.player_data.get_stat(author.id, "Received")
        giver_id = await self.client.player_data.get_stat(author.id, "Giver")
        giver = await self.client.fetch_user(giver_id)

        # check to see if author and player can be DMs
        if await self.client.player_data.cant_dm_user(author):
            await SendEmbed.send_cant_dm_author(channel)

        if await self.client.player_data.cant_dm_user(giver):
            await SendEmbed.send_cant_dm_player(giver, channel)

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(author, channel.id, server):
            return

        # check if author is dead and trying to decline
        # if the results are true then author is dead and return
        if await GetSetStats.get_stat(author.id, "Dead"):
            await SendEmbed.send_author_d(author, channel)
            return

        # add author to the players.json if not yet added
        await self.client.player_data.add_player(ctx.author)

        # if there is no gift to decline
        if gift_type is False:
            await SendEmbed.send_udt_nothing(author, channel)

        # if the gift unboxed was a nice gift
        elif gift_type == "nice" and giver_id is not False:
            # update the stats for unboxing devious gifts
            await GetSetStats.update_unbox_devious_stats(author.id, giver_id)

            # send the message
            await SendEmbed.send_decline_nice(author, channel, giver)

            # add giver to json
            await self.client.highscore_handling.add_highscore(giver)
            await GetSetHighscores.update_highscore(giver.id)

        elif gift_type == "devious" and giver_id is not False:
            # update the stats for declining devious gifts
            await GetSetStats.update_decline_devious_stats(author.id, giver_id)

            # send the message
            await SendEmbed.send_decline_devious(author, channel, giver)

            dead_role = get(server.roles, name=settings.dead_role_NAME)
            await giver.add_roles(dead_role)

            # add author to json
            await self.client.highscore_handling.add_highscore(author)
            await GetSetHighscores.update_highscore(author.id)

    @commands.command()
    async def trash(self, ctx):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # get the type of gift trashed and get the giver id
        gift_type = await self.client.player_data.get_stat(author.id, "Received")
        giver_id = await self.client.player_data.get_stat(author.id, "Giver")
        trashability_amt = await self.client.player_data.get_stat(author.id, "Trashability")
        giver = await self.client.fetch_user(giver_id)

        # check to see if author and player can be DMs
        if await self.client.player_data.cant_dm_user(author):
            await SendEmbed.send_cant_dm_author(channel)

        if await self.client.player_data.cant_dm_user(giver):
            await SendEmbed.send_cant_dm_player(giver, channel)

        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(author, channel.id, server):
            return

        # check if author is dead and trying to trash
        # if the results are true then author is dead and return
        if await GetSetStats.get_stat(author.id, "Dead"):
            await SendEmbed.send_author_d(author, channel)
            return

        # add author to the players.json if not yet added
        await self.client.player_data.add_player(author)

        # if there is no gift to trash
        if gift_type is False:
            await SendEmbed.send_udt_nothing(author, channel)

        # not enough trashability to trash the gift
        elif not trashability_amt and giver_id is not False:
            await SendEmbed.send_no_trashability(author, channel, giver)

        # successfully throw away the gift if author has trashability
        elif trashability_amt and giver_id is not False:
            # update the stats for trashing gifts
            await GetSetStats.update_trashing_stats(author.id)
            # send the message
            await SendEmbed.send_trashed_gift(author, channel, giver, gift_type)


# cog set up
async def setup(client):
    await client.add_cog(GuestCommands(client))
