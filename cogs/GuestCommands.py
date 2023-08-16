import discord
from discord.ext import commands
from discord.utils import get
import DataHelper
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
        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # check if author is dead and trying to unbox
        # if the results are true then author is dead and return
        # (yes pass in author twice, but it doesn't ever matter)
        if await self.client.death_handling.check_death(ctx.channel, ctx.author, ctx.author):
            return

        # add author to the players.json if not yet added
        await self.client.player_data.add_player(ctx.author)
        author_id = ctx.author.id

        # get the type of gift unboxed and get the giver id
        gift_type = await self.client.player_data.get_stat(author_id, "Received")
        giver_id = await self.client.player_data.get_stat(author_id, "Giver")
        giver = await self.client.fetch_user(giver_id)

        # if there is no gift to unbox
        if gift_type is False:
            await SendEmbed.send_udt_nothing(ctx.author, ctx.channel)

        # if the gift unboxed was a nice gift
        elif gift_type == "nice" and giver_id is not False:

            # update the stats for unboxing nice gifts
            await self.client.player_data.update_unbox_nice_stats(author_id, giver_id)
            # send the message
            await SendEmbed.send_unbox_nice(ctx.author, ctx.channel)

            # TODO
            # await highscore stuff(giver)
            # giver = await self.client.fetch_user(giver_id)
            #
            # await self.client.player_data.add_high_score(ctx.author)
            # await self.client.player_data.add_high_score(giver)
            # await DataHelper.update_high_score(ctx.author.id, 1, False, "Old Score")
            # scores = await DataHelper.get_high_score_data()
            #
            # if int(scores[str(ctx.author.id)]["Old Score"]) > int(scores[str(ctx.author.id)]["New Score"]):
            #     old_score = int(scores[str(ctx.author.id)]["Old Score"])
            #
            #     await DataHelper.update_high_score(ctx.author.id, old_score, True, "New Score")
            #
            # return

        elif gift_type == "devious" and giver_id is not False:

            # update the stats for unboxing devious gifts
            await self.client.player_data.update_unbox_devious_stats(author_id, giver_id)
            # send the message
            await SendEmbed.send_unbox_devious(ctx.author, ctx.channel, giver)

            # give the author the dead role
            dead_role = get(ctx.guild.roles, name=settings.dead_role_NAME)
            await ctx.author.add_roles(dead_role)

            # TODO
            # await self.client.player_data.add_high_score(ctx.author)
            # await self.client.player_data.add_high_score(giver)
            # await DataHelper.update_high_score(giver.id, 1, False, "Old Score")
            # await DataHelper.update_high_score(ctx.author.id, 1, False, "Deaths")
            # scores = await DataHelper.get_high_score_data()
            # if int(scores[str(giver.id)]["Old Score"]) > int(scores[str(giver.id)]["New Score"]):
            #     await DataHelper.update_high_score(giver.id, int(scores[str(giver.id)]["Old Score"]), True, "New Score")

            win = await DataHelper.check_winner()
            if win:
                # final leaderboard is dark gold
                # title, name_list, value_list, status = await make_leaderboard(True)
                # em_board = discord.Embed(title=title, color=discord.Color.orange())
                # for num in range(len(name_list)):
                #     em_board.add_field(name=name_list[num],
                #                        value=value_list[num] + " \n" + status[num])
                # first_name = name_list[0]
                # first_score = value_list[0]
                # # winner announcement is gold
                # em_announce = discord.Embed(color=discord.Color.gold())
                # em_announce.add_field(name=f"Everyone has playing has died! **{first_name} WINS!!**",
                #                       value=f"With a final score of {first_score}")
                # em_announce.set_footer(text=f"The leaderboard is reset, and everyone came back to life")
                # await ctx.channel.send(embed=em_announce)
                # await ctx.channel.send(embed=em_board)
                # users = await get_player_data()
                # for player_id in users.keys():
                #     member_obj = await make_member(player_id)
                #     for roles in member_obj.roles:
                #         remove_role, role_name = await dead_person(roles.id, "remove role")
                #         if remove_role:
                #             dead_role = get(ctx.guild.roles, name=role_name)
                #             await member_obj.remove_roles(dead_role)
                #             await reset_data()
                #             self.client.get_command("visit").reset_cooldown(ctx)

                em_gift = discord.Embed(color=discord.Color.magenta())
                em_gift.add_field(name=f"{giver} is the only player alive!",
                                  value="The game will reset at the end of the day")
                await ctx.channel.send(embed=em_gift)

    @commands.command()
    async def decline(self, ctx):
        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # check if author is dead and trying to unbox
        # if the results are true then author is dead and return
        # (yes pass in author twice, but it doesn't ever matter)
        if await self.client.death_handling.check_death(ctx.channel, ctx.author, ctx.author):
            return

        # add author to the players.json if not yet added
        await self.client.player_data.add_player(ctx.author)
        author_id = ctx.author.id

        # get the type of gift unboxed and get the giver id
        gift_type = await self.client.player_data.get_stat(author_id, "Received")
        giver_id = await self.client.player_data.get_stat(author_id, "Giver")
        giver = await self.client.fetch_user(giver_id)

        # if there is no gift to decline
        if gift_type is False:
            await SendEmbed.send_udt_nothing(ctx.author, ctx.channel)

        # if the gift unboxed was a nice gift
        elif gift_type == "nice" and giver_id is not False:
            # update the stats for unboxing devious gifts
            await self.client.player_data.update_unbox_devious_stats(author_id, giver_id)

            # send the message
            await SendEmbed.send_decline_nice(ctx.author, ctx.channel, giver)

            # TODO
            # await self.client.player_data.add_high_score(ctx.author)
            # await self.client.player_data.add_high_score(giver)
            # await DataHelper.update_high_score(giver_id, 1, False, "Old Score")
            # scores = await DataHelper.get_high_score_data()
            # if int(scores[str(giver_id)]["Old Score"]) > int(scores[str(giver_id)]["New Score"]):
            #     await DataHelper.update_high_score(giver.id, int(scores[str(giver_id)]["Old Score"]), True, "New Score")

        elif gift_type == "devious" and giver_id is not False:
            # update the stats for declining devious gifts
            await self.client.player_data.update_decline_devious_stats(author_id, giver_id)

            # send the message
            await SendEmbed.send_decline_devious(ctx.author, ctx.channel, giver)

            # give the giver the dead role
            giver_obj = await self.client.player_data.make_member(giver_id)
            dead_role = get(ctx.guild.roles, name=settings.dead_role_NAME)
            await giver_obj.add_roles(dead_role)

            # TODO
            # await self.client.player_data.add_high_score(ctx.author)
            # await self.client.player_data.add_high_score(giver)
            # await DataHelper.update_high_score(ctx.author.id, 1, False, "Old Score")
            # await DataHelper.update_high_score(giver_id, 1, False, "Deaths")
            # scores = await DataHelper.get_high_score_data()
            # if int(scores[str(ctx.author.id)]["Old Score"]) > int(scores[str(ctx.author.id)]["New Score"]):
            #     await DataHelper.update_high_score(ctx.author.id, int(scores[str(ctx.author.id)]["Old Score"]), True,
            #                                        "New Score")

            win = await DataHelper.check_winner()
            if win:
                # final leaderboard is dark gold
                # title, name_list, value_list, status = await make_leaderboard(True)
                # em_board = discord.Embed(title=title, color=discord.Color.orange())
                # for num in range(len(name_list)):
                #     em_board.add_field(name=name_list[num],
                #                        value=value_list[num] + " \n" + status[num])
                # first_name = name_list[0]
                # first_score = value_list[0]
                # # winner announcement is gold
                # em_announce = discord.Embed(color=discord.Color.gold())
                # em_announce.add_field(name=f"Everyone has playing has died! **{first_name} WINS!!**",
                #                       value=f"With a final score of {first_score}")
                # em_announce.set_footer(text=f"The leaderboard is reset, and everyone came back to life")
                # await ctx.channel.send(embed=em_announce)
                # await ctx.channel.send(embed=em_board)
                # users = await get_player_data()
                # for player_id in users.keys():
                #     member_obj = await make_member(player_id)
                #     for roles in member_obj.roles:
                #         remove_role, role_name = await dead_person(roles.id, "remove role")
                #         if remove_role:
                #             dead_role = get(ctx.guild.roles, name=role_name)
                #             await member_obj.remove_roles(dead_role)
                #             await reset_data()
                #             self.client.get_command("visit").reset_cooldown(ctx)

                em_gift = discord.Embed(color=discord.Color.magenta())
                em_gift.add_field(name=f"{ctx.author} is the only player alive!",
                                  value="The game will reset at the end of the day")
                await ctx.channel.send(embed=em_gift)

    @commands.command()
    async def trash(self, ctx):
        # check if the command is sent in wrong chat
        # if the results are true, then it was sent in wrong place and return and reset cooldown
        if await self.client.wrong_chat.check_guest_wc(ctx.channel.id, ctx.guild, ctx.author):
            return

        # check if author is dead and trying to unbox
        # if the results are true then author is dead and return
        # (yes pass in author twice, but it doesn't ever matter)
        if await self.client.death_handling.check_death(ctx.channel, ctx.author, ctx.author):
            return

        # add author to the players.json if not yet added
        await self.client.player_data.add_player(ctx.author)
        author_id = ctx.author.id

        # get the type of gift unboxed and get the giver id
        gift_type = await self.client.player_data.get_stat(author_id, "Received")
        giver_id = await self.client.player_data.get_stat(author_id, "Giver")
        trashability_amt = await self.client.player_data.get_stat(author_id, "Trashability")
        giver = await self.client.fetch_user(giver_id)

        # if there is no gift to trash
        if gift_type is False:
            await SendEmbed.send_udt_nothing(ctx.author, ctx.channel)

        # not enough trashability to trash the gift
        elif not trashability_amt and giver_id is not False:
            await SendEmbed.send_no_trashability(ctx.author, ctx.channel, giver)

        # throw away the gift if author has trashability
        elif trashability_amt and giver_id is not False:
            # update the stats for trashing gifts
            await self.client.player_data.update_trashing_stats(author_id)
            # send the message
            await SendEmbed.send_trashed_gift(ctx.author, ctx.channel, giver, gift_type)


# cog set up
async def setup(client):
    await client.add_cog(GuestCommands(client))
