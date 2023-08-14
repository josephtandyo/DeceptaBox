import discord
from discord.ext import commands
from discord.utils import get
import DataHelper


class GuestCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("GuestCommands Cog is ready")

    @commands.command()
    async def unbox(self, ctx):
        # !unbox is server specific command
        # Wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Guest")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # Checking if player is dead. Role specific.
        for role in ctx.author.roles:
            dead_unboxing = await DataHelper.dead_person(role.id, "dead unboxing")
            if dead_unboxing:
                em_dead = discord.Embed(color=discord.Color.red())
                em_dead.add_field(name="R.I.P", value=dead_unboxing, inline=True)
                em_dead.set_footer(text=f"{ctx.author} tried to unbox a gift")
                await ctx.channel.send(embed=em_dead)
                return

        await self.client.player_data.add_player(ctx.author)
        user = ctx.author
        users = await DataHelper.get_player_data()
        gift_type = users[str(user.id)]["Received"]
        giver_id = users[str(user.id)]["Giver"]

        if gift_type == "nice" and giver_id is not False:
            await DataHelper.update_stats(ctx.author.id, 1, False, "Total Points")
            await DataHelper.update_stats(ctx.author.id, 1, False, "Unboxed Points")
            await DataHelper.update_stats(ctx.author.id, 1, False, "Trashability")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Received")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Giver")
            await DataHelper.update_stats(ctx.author.id, 0, True, "Join")
            await DataHelper.update_stats(giver_id, 0, True, "Join")

            # earning a point is fuchsia
            em_unbox = discord.Embed(color=discord.Color.fuchsia())
            em_unbox.add_field(name=f"**{ctx.author.name}** unboxed a **nice gift!**",
                               value=f"**{ctx.author.name}** receives **1 point** and **1 trashability**")
            em_unbox.set_footer(text=f"{ctx.author} unboxed a gift")
            await ctx.channel.send(embed=em_unbox)
            giver = await self.client.fetch_user(giver_id)

            await self.client.player_data.add_high_score(ctx.author)
            await self.client.player_data.add_high_score(giver)
            await DataHelper.update_high_score(ctx.author.id, 1, False, "Old Score")
            scores = await DataHelper.get_high_score_data()

            if int(scores[str(ctx.author.id)]["Old Score"]) > int(scores[str(ctx.author.id)]["New Score"]):
                old_score = int(scores[str(ctx.author.id)]["Old Score"])

                await DataHelper.update_high_score(ctx.author.id, old_score, True, "New Score")

            return

        elif gift_type == "devious" and giver_id is not False:
            giver = await self.client.fetch_user(giver_id)
            await DataHelper.update_stats(giver_id, 1, False, "Total Points")
            await DataHelper.update_stats(giver_id, 1, False, "Kill Points")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Received")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Giver")
            await DataHelper.update_stats(ctx.author.id, 0, True, "Dead")
            await DataHelper.update_stats(ctx.author.id, 0, True, "Join")
            await DataHelper.update_stats(giver_id, 0, True, "Join")

            em_bomb = discord.Embed(color=discord.Color.default())
            em_bomb.add_field(name=f"**{ctx.author.name}** unboxed an explosive **devious gift** and **dies!**",
                              value=f"**{giver.name}** receives **1 point**")
            em_bomb.set_footer(text=f"{ctx.author} unboxed a gift")
            await ctx.channel.send(embed=em_bomb)

            dead_role = get(ctx.guild.roles, name="Dead")
            await ctx.author.add_roles(dead_role)

            await self.client.player_data.add_high_score(ctx.author)
            await self.client.player_data.add_high_score(giver)
            await DataHelper.update_high_score(giver.id, 1, False, "Old Score")
            await DataHelper.update_high_score(ctx.author.id, 1, False, "Deaths")
            scores = await DataHelper.get_high_score_data()
            if int(scores[str(giver.id)]["Old Score"]) > int(scores[str(giver.id)]["New Score"]):
                await DataHelper.update_high_score(giver.id, int(scores[str(giver.id)]["Old Score"]), True, "New Score")

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

        # no present to unbox is dark orange
        elif gift_type is False:
            em_gift = discord.Embed(color=discord.Color.red())
            em_gift.add_field(name="Inventory is empty!",
                              value="You need to `!visit` a player and receive a gift first to unbox it")
            em_gift.set_footer(text=f"{ctx.author} tried to unbox a gift")

            await ctx.channel.send(embed=em_gift)

    @commands.command()
    async def decline(self, ctx):
        # same colors as before
        # Wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Guest")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # Checking if player is dead. Role specific.
        for role in ctx.author.roles:
            dead_unboxing = await DataHelper.dead_person(role.id, "dead declining")
            if dead_unboxing:
                em_dead = discord.Embed(color=discord.Color.red())
                em_dead.add_field(name="R.I.P", value=dead_unboxing, inline=True)
                em_dead.set_footer(text=f"{ctx.author} tried to decline a gift")
                await ctx.channel.send(embed=em_dead)
                return

        await self.client.player_data.add_player(ctx.author)
        user = ctx.author
        users = await DataHelper.get_player_data()
        gift_type = users[str(user.id)]["Received"]
        giver_id = users[str(user.id)]["Giver"]

        if gift_type == "nice" and giver_id is not False:
            giver = await self.client.fetch_user(giver_id)
            await DataHelper.update_stats(giver_id, 1, False, "Total Points")
            await DataHelper.update_stats(giver_id, 1, False, "Declined Points")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Received")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Giver")
            await DataHelper.update_stats(ctx.author.id, 0, True, "Join")
            await DataHelper.update_stats(giver_id, 0, True, "Join")

            # dark gray
            em_decline = discord.Embed(color=discord.Color.default())
            em_decline.add_field(name=f"**{ctx.author.name}** declined a **nice gift!**",
                                 value=f"**{giver.name}** receives **1 point**")
            em_decline.set_footer(text=f"{ctx.author} declined a gift")
            await ctx.channel.send(embed=em_decline)

            await self.client.player_data.add_high_score(ctx.author)
            await self.client.player_data.add_high_score(giver)
            await DataHelper.update_high_score(giver_id, 1, False, "Old Score")
            scores = await DataHelper.get_high_score_data()
            if int(scores[str(giver_id)]["Old Score"]) > int(scores[str(giver_id)]["New Score"]):
                await DataHelper.update_high_score(giver.id, int(scores[str(giver_id)]["Old Score"]), True, "New Score")

        elif gift_type == "devious" and giver_id is not False:
            giver = await self.client.fetch_user(giver_id)
            await DataHelper.update_stats(ctx.author.id, 1, False, "Total Points")
            await DataHelper.update_stats(ctx.author.id, 1, False, "Accidental Kill")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Received")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Giver")
            await DataHelper.update_stats(giver_id, 0, True, "Dead")
            await DataHelper.update_stats(ctx.author.id, 0, True, "Join")
            await DataHelper.update_stats(giver_id, 0, True, "Join")

            em_bomb = discord.Embed(color=discord.Color.fuchsia())
            em_bomb.add_field(
                name=f"**{ctx.author.name}** declined an explosive **devious gift** and receives **1 point**!",
                value=f"**{giver.name}** receives a bomb and **dies**")
            em_bomb.set_footer(text=f"{ctx.author} declined a gift")
            await ctx.channel.send(embed=em_bomb)

            giver_obj = await self.client.player_data.make_member(giver_id)
            dead_role = get(ctx.guild.roles, name="Dead")
            await giver_obj.add_roles(dead_role)

            await self.client.player_data.add_high_score(ctx.author)
            await self.client.player_data.add_high_score(giver)
            await DataHelper.update_high_score(ctx.author.id, 1, False, "Old Score")
            await DataHelper.update_high_score(giver_id, 1, False, "Deaths")
            scores = await DataHelper.get_high_score_data()
            if int(scores[str(ctx.author.id)]["Old Score"]) > int(scores[str(ctx.author.id)]["New Score"]):
                await DataHelper.update_high_score(ctx.author.id, int(scores[str(ctx.author.id)]["Old Score"]), True,
                                                   "New Score")

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

        # no present to unbox is dark orange
        elif gift_type is False:
            em_gift = discord.Embed(color=discord.Color.red())
            em_gift.add_field(name="Inventory is empty!",
                              value="You need to `!visit` a player and receive a gift first to decline it")
            em_gift.set_footer(text=f"{ctx.author} tried to decline a gift")
            await ctx.channel.send(embed=em_gift)

    @commands.command()
    async def trash(self, ctx):
        # Wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Guest")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # Checking if player is dead. Role specific.
        for role in ctx.author.roles:
            dead_unboxing = await DataHelper.dead_person(role.id, "dead trashing")
            if dead_unboxing:
                em_dead = discord.Embed(color=discord.Color.red())
                em_dead.add_field(name="R.I.P", value=dead_unboxing, inline=True)
                em_dead.set_footer(text=f"{ctx.author} tried to trash a gift")
                await ctx.channel.send(embed=em_dead)
                return

        await self.client.player_data.add_player(ctx.author)
        user = ctx.author
        users = await DataHelper.get_player_data()
        gift_type = users[str(user.id)]["Received"]
        giver_id = users[str(user.id)]["Giver"]
        trash_cap = users[str(user.id)]["Trashability"]

        if gift_type is False:
            em_empty = discord.Embed(color=discord.Color.red())
            em_empty.add_field(name="Inventory is empty!",
                               value="You need to `!visit` a player and receive a gift first to trash it")
            em_empty.set_footer(text=f"{ctx.author} tried to trash a gift")
            await ctx.channel.send(embed=em_empty)

        # throwing gift away is teal
        elif trash_cap and giver_id is not False:
            giver = await self.client.fetch_user(giver_id)
            await DataHelper.update_stats(ctx.author.id, -1, False, "Trashability")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Received")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Giver")

            em_trash = discord.Embed(color=discord.Color.green())
            em_trash.add_field(name=f"You threw away {giver.name}'s {gift_type} gift!",
                               value=f"**Trashability** decreased by 1")
            em_trash.set_footer(text=f"{ctx.author} trashed a gift")
            await ctx.channel.send(embed=em_trash)

        # not enough trash cap is dark teal
        elif not trash_cap and giver_id is not False:
            giver = await self.client.fetch_user(giver_id)
            em_none = discord.Embed(color=discord.Color.red())
            em_none.add_field(name=f"Not enough **trashability** to throw away {giver.name}'s gift!",
                              value="You need at least **1 trashability** which can be gained from unboxing **nice "
                                    "gifts**")
            em_none.set_footer(text=f"{ctx.author} tried to trash a gift")

            await ctx.channel.send(embed=em_none)


async def setup(client):
    await client.add_cog(GuestCommands(client))
