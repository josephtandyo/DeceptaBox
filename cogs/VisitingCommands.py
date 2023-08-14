import discord
from discord.ext import commands

import DataHelper


class VisitingCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("VisitingCommands is ready")

    # change the timer
    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 0, commands.BucketType.user)
    async def visit(self, ctx, member: discord.Member):
        # !visit is server specific command
        # Wrong chat is brand red
        await member.send("bruh")
        print(member.id)

        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Guest")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # Visiting bot is purple
        elif member == self.client.user:
            em_bot_visit = discord.Embed(color=discord.Color.purple())
            em_bot_visit.add_field(
                name="Thanks for coming, I have nothing for you though. Try visiting **players**",
                value="I will teleport you back to where you were")
            em_bot_visit.set_footer(text=f"{ctx.author} arrived at {self.client.user}'s home")
            await ctx.author.send(embed=em_bot_visit)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        await self.client.player_data.add_player(ctx.author)
        await self.client.player_data.add_player(member)

        # Checking if player is dead. Role specific.
        for role in ctx.author.roles:
            dead_visiting = await DataHelper.dead_person(role.id, "dead visiting")
            if dead_visiting:
                em_dead_a = discord.Embed(color=discord.Color.red())
                em_dead_a.add_field(name="R.I.P", value=dead_visiting, inline=True)
                em_dead_a.set_footer(text=f"{ctx.author} tried to visit {member}")
                await ctx.channel.send(embed=em_dead_a)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

        # Checking if player visiting is dead. Role specific.
        for role in member.roles:
            visiting_dead = await DataHelper.dead_person(role.id, "visiting dead")
            if visiting_dead:
                em_dead_m = discord.Embed(color=discord.Color.red())
                em_dead_m.add_field(name="R.I.P", value=visiting_dead, inline=True)
                em_dead_m.set_footer(text=f"{ctx.author} tried to visit {member}")
                await ctx.channel.send(embed=em_dead_m)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

        # Visiting yourself is dark green
        if member == ctx.author:
            em_self = discord.Embed(color=discord.Color.red())
            em_self.add_field(name="You can't visit yourself!",
                              value="How is that possible??")
            em_self.set_footer(text=f"{ctx.author} tried to visit themselves")
            await ctx.channel.send(embed=em_self)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # Visiting no one is dark green
        elif member is None:
            em_none = discord.Embed(color=discord.Color.red())
            em_none.add_field(name="You have not specified who you are visiting!",
                              value="To visit a host, type the command and mention the player you want to visit")
            em_none.set_footer(text=f"{ctx.author} tried to visit no one")
            await ctx.channel.send(embed=em_none)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        users = await DataHelper.get_player_data()
        print(users)

        inventory_full = users[str(ctx.author.id)]["Received"]
        already_visiting = users[str(ctx.author.id)]["Visiting"]
        guest_at_home = users[str(ctx.author.id)]["Visited"]
        guest_at_host = users[str(member.id)]["Visited"]
        not_home = users[str(member.id)]["Visiting"]

        print("will this print?")

        # When the player is already at someone else's house, the color is dark green
        if already_visiting:
            user_visiting = await self.client.fetch_user(already_visiting)
            if member != user_visiting:
                em_else = discord.Embed(color=discord.Color.red())
                em_else.add_field(name=f"You are already at {user_visiting.name}'s house!",
                                  value=f"If you want to visit {member.name} instead, you need to go home first")
                em_else.set_footer(text=f"{ctx.author} tried to visit {member}")
                await ctx.channel.send(embed=em_else)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

            elif member == user_visiting:
                em_here = discord.Embed(color=discord.Color.red())
                em_here.add_field(name=f"You have arrived at {user_visiting.name}'s house a long time ago!",
                                  value=f"Wait for {user_visiting.name} to pick a gift for you, or if you don't want to"
                                        f" wait, "
                                        f"go home")
                em_here.set_footer(text=f"{ctx.author} tried to visit {user_visiting}")
                await ctx.channel.send(embed=em_here)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

        # When a player is already at their house, the color is dark green
        elif guest_at_host:
            guest_inside = await self.client.fetch_user(guest_at_host)
            em_full = discord.Embed(color=discord.Color.red())
            em_full.add_field(name=f"{member.name}'s house is full, as {guest_inside.name} is already there!",
                              value=f"Visit {member.name} at a later time or visit somebody else")
            em_full.set_footer(text=f"{ctx.author} tried to visit {member}")
            await ctx.channel.send(embed=em_full)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        elif guest_at_home:
            guest_inside = await self.client.fetch_user(guest_at_home)
            em_leave = discord.Embed(color=discord.Color.red())
            em_leave.add_field(name=f"{guest_inside.name} is at your house!",
                               value=f"Give {guest_inside.name} a gift first before you "
                                     f"are able to visit {member.name}")
            em_leave.set_footer(text=f"{ctx.author} tried to visit {member}")
            await ctx.channel.send(embed=em_leave)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        elif not_home:
            host_elsewhere = await self.client.fetch_user(not_home)
            em_empty = discord.Embed(color=discord.Color.red())
            em_empty.add_field(name=f"{member.name} is at {host_elsewhere.name}'s house!",
                               value=f"Wait for {member.name} to return home before visiting {member.name}")
            em_empty.set_footer(text=f"{ctx.author} tried to visit {member}")
            await ctx.channel.send(embed=em_empty)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # When you still have a gift in inventory, the color is dark green
        elif inventory_full:
            em_gift = discord.Embed(color=discord.Color.red())
            em_gift.add_field(name="Your inventory is full!",
                              value=f"Unbox, decline or trash the previous gift before visiting {member.name}")
            em_gift.set_footer(text=f"{ctx.author} tried to visit {member}")
            await ctx.channel.send(embed=em_gift)
            self.client.get_command("visit").reset_cooldown(ctx)
            return

        # Visiting a valid player is green
        else:
            await DataHelper.update_stats(member.id, 0, ctx.author.id, "Visited")
            await DataHelper.update_stats(ctx.author.id, 0, member.id, "Visiting")

            em_host = discord.Embed(color=discord.Color.blue())
            em_host.add_field(name=f"{ctx.author.name} has come to visit!",
                              value=f"Choose a `!nice` or a `!devious` gift for {ctx.author.name}")
            em_host.set_footer(text=f"{ctx.author} arrived at {member}'s home")
            await member.send(embed=em_host)

            em_guest = discord.Embed(color=discord.Color.green())
            em_guest.add_field(name=f"You have arrived!",
                               value=f"Now wait as {member.name} will pick the perfect gift for you...")
            em_guest.set_footer(text=f"{ctx.author} is waiting for a gift at {member}'s home")
            await ctx.channel.send(embed=em_guest)

    @commands.command()
    async def home(self, ctx):
        # !visit is server specific command
        # Wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Guest")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # Checking if player is dead. Role specific.
        for role in ctx.author.roles:
            dead_visiting = await DataHelper.dead_person(role.id, "dead home")
            if dead_visiting:
                em_dead = discord.Embed(color=discord.Color.red())
                em_dead.add_field(name="R.I.P", value=dead_visiting, inline=True)
                em_dead.set_footer(text=f"{ctx.author} tried to go home")
                await ctx.channel.send(embed=em_dead)
                self.client.get_command("visit").reset_cooldown(ctx)
                return

        await self.client.player_data.add_player(ctx.author)
        users = await DataHelper.get_player_data()
        gift_type = users[str(ctx.author.id)]["Received"]
        already_visiting = users[str(ctx.author.id)]["Visiting"]

        # When the player is home, the color is dark green
        if not already_visiting:
            em_home = discord.Embed(color=discord.Color.red())
            em_home.add_field(name="You are already home!",
                              value="Visit someone first and then you can decide to go home")
            em_home.set_footer(text=f"{ctx.author} tried to go home")
            await ctx.channel.send(embed=em_home)
            return

        # When you have a gift in inventory, the color is dark green
        elif gift_type:
            em_gift = discord.Embed(color=discord.Color.red())
            em_gift.add_field(name="The host has given you a gift already!",
                              value="You cannot leave their house until you unbox, decline or trash the gift")
            em_gift.set_footer(text=f"{ctx.author} tried to go home")
            await ctx.channel.send(embed=em_gift)
            return

        # Able to leave
        else:
            for player_id in users.keys():
                if int(player_id) == int(users[str(ctx.author.id)]["Visiting"]):
                    member_obj = await self.client.player_data.make_member(int(player_id))
                    await DataHelper.update_stats(ctx.author.id, 0, False, "Visiting")
                    await DataHelper.update_stats(member_obj.id, 0, False, "Visited")

                    em_host = discord.Embed(color=discord.Color.blue())
                    em_host.add_field(name=f"{ctx.author.name} has went home :(",
                                      value=f"You took too long to give them a gift, "
                                            f"{ctx.author.name} got tired of waiting")
                    em_host.set_footer(text=f"{ctx.author} went home")
                    await member_obj.send(embed=em_host)

                    em_guest = discord.Embed(color=discord.Color.green())
                    em_guest.add_field(name=f"You have arrived home from {member_obj.name}'s house",
                                       value=f"You can visit a host")
                    em_guest.set_footer(text=f"{ctx.author} went home")
                    await ctx.channel.send(embed=em_guest)
                    self.client.get_command("visit").reset_cooldown(ctx)


async def setup(client):
    await client.add_cog(VisitingCommands(client))
