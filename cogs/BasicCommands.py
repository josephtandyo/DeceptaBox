import discord
from discord.ext import commands

import DataHelper


class BasicCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_start(self):
        print("BasicCommands Cog is ready")

    @commands.command()
    async def rules(self, ctx):
        # !rules are channel specific and in DM of bot
        # Wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Basic")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # Rules and commands are og_blurple
        em_rules = discord.Embed(title="Here are the Basic Rules:", color=discord.Color.og_blurple())
        em_rules.add_field(name="The Main Goal is to Earn as Many Points as Possible Without Dying!",
                           value="\n"  # how many minutes
                                 "\n**1.** Every idk minutes, you may **visit** other players and act as the guest\n"
                                 "\n**2.** The player you visited will act as the host\n"
                                 "\n**3.** The host will have the option to give the guest a **nice** gift or a "
                                 "**devious** gift\n "
                                 "> *The guest can go back **home** if the host hasn't given them a gift yet*\n"
                                 "\n**4.** After receiving a gift, the guest can **unbox**, **decline** or **trash** "
                                 "the"
                                 "gift "
                                 "\n> Unboxing a **nice gift**: The guest will gain **1 point** and **1 trashability**"
                                 "\n> Unboxing a **devious gift**: The guest will **DIE** and the host will gain **1 "
                                 "point**\n> "
                                 "\n> Declining a **nice gift**: The host will gain **1 point**"
                                 "\n> Declining a **devious gift**: The host will **DIE** and the guest will gain **1 "
                                 "point**\n> "
                                 "\n> Thrashing **ANY gift**: The gift is forever **GONE**; the gift type will be "
                                 "revealed"
                                 "\n>> *Trashing a gift will use up **1 trashability***\n "
                                 "\n**5.** If a player visits you, they will act as the guest and you will act as the "
                                 "host\n")
        em_rules.set_footer(text="You can only visit and get visited by one player at a time\n"
                                 "You can't visit anyone while a gift has not been unboxed, declined or trashed\n"
                                 ">> For the list of commands, type `!guide`")

        await ctx.channel.send(embed=em_rules)

    @commands.command()
    async def guide(self, ctx):
        # !guide are channel specific and in DM of bot
        # Wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Basic")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # Rules and commands are og_blurple
        em_commands = discord.Embed(title="Commands Guide", color=discord.Color.blurple())
        em_commands.add_field(name="Basic Commands:",
                              value="*Use in the Server and DM*\n\n"
                                    "**`!guide`**\n"
                                    "To see the commands\n\n"
                                    "**`!rules`**\n"
                                    "To see the rules\n\n"
                                    "**`!stats (@...)`**\n"
                                    "To see points and \n"
                                    "trashability\n\n"
                                    "**`!leaderboards`**\n"
                                    "To see the current \n"
                                    "leaderboard\n\n"
                                    "**`!highscores`**\n"
                                    "To see the current \n"
                                    "high scores")
        em_commands.add_field(name="Guest Commands:",
                              value="*Use in the Server*\n\n"
                                    "**`!visit @...`**\n"
                                    "To visit other players\n\n"
                                    "**`!home`**\n"
                                    "To go back home\n\n"
                                    "**`!unbox`**\n"
                                    "To unbox the gift\n\n"
                                    "**`!decline`**\n"
                                    "To decline the gift\n\n"
                                    "**`!trash`**\n"
                                    "To trash the gift")
        em_commands.add_field(name="Host Commands:",
                              value="*Use in the DM*\n\n"
                                    "**`!devious`**\n"
                                    "To give a devious gift\n\n"
                                    "**`!nice`**\n"
                                    "To give a nice gift\n\n")

        await ctx.channel.send(embed=em_commands)

    # update stats
    @commands.command()
    async def stats(self, ctx, member: discord.Member = None):
        # !stats are channel specific and in DM of bot
        # Wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Basic")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # Checking stats of bot is purple
        if member == self.client.user:
            em_bot_stat = discord.Embed(title="Present Delivery Bot's Stats", color=discord.Color.purple())
            em_bot_stat.add_field(name="Total Points", value=999)
            em_bot_stat.set_footer(text=f"Requested by: {ctx.author}")
            await ctx.send(embed=em_bot_stat)
            return

        # Checking own stats is magenta
        elif member is None or member == ctx.author:
            await self.client.player_data.add_player(ctx.author)
            user = ctx.author
            users = await DataHelper.get_player_data()

        # Checking other player's stats is dark magenta
        else:
            await self.client.player_data.add_player(member)
            user = member
            users = await DataHelper.get_player_data()

        total = users[str(user.id)]["Total Points"]
        trashability = users[str(user.id)]["Trashability"]
        nice_amt = users[str(user.id)]["Unboxed Points"]
        decline_amt = users[str(user.id)]["Declined Points"]
        kills_amt = users[str(user.id)]["Kill Points"]
        accident_amt = users[str(user.id)]["Accidental Kill"]

        em_stat = discord.Embed(title=f"{user}'s Stats", color=discord.Color.teal())
        em_stat.add_field(name="General Stats",
                          value="*Overall*\n\n"
                                "**Total Points:**\n"
                                f"{total}\n\n"
                                "**Trashability:**\n"
                                f"{trashability}", inline=True)
        em_stat.add_field(name="Guest Stats",
                          value="*Points Gained as a Guest*\n\n"
                                "**Opened Gift Points:**\n"
                                f"{nice_amt}\n\n"
                                "**Killing Hosts Points:**\n"
                                f"{accident_amt}", inline=True)

        em_stat.add_field(name="Host Stats",
                          value="*Points Gained as a Host*\n\n"
                                "**Returned Gift Points:**\n"
                                f"{decline_amt}\n\n"
                                "**Killing Guests Points:**\n"
                                f"{kills_amt}", inline=True)

        em_stat.set_footer(text=f"Requested by: {ctx.author}")
        await ctx.send(embed=em_stat)

    @commands.command()
    async def leaderboards(self, ctx):
        # channel specific and wrong chat color is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Basic")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # current leaderboard is dark gold
        title, name_list, value_list, status = await self.client.player_data.make_leaderboard()

        em_board = discord.Embed(title=title, color=discord.Color.orange())

        for num in range(len(name_list)):
            em_board.add_field(name=name_list[num],
                               value=value_list[num] + " \n" + status[num])

        await ctx.channel.send(embed=em_board)

    @commands.command()
    async def highscores(self, ctx):
        # channel specific and wrong chat color is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Basic")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # current leaderboard is dark gold
        name_list, value_list, death_list = await self.client.player_data.make_highscores()

        em_board = discord.Embed(title="The Current High Scores: ", color=discord.Color.orange())

        for num in range(len(name_list)):
            em_board.add_field(name=name_list[num],
                               value=value_list[num] + " \n" + death_list[num])

        await ctx.channel.send(embed=em_board)


async def setup(client):
    await client.add_cog(BasicCommands(client))
