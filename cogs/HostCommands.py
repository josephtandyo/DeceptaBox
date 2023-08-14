from discord.ext import commands
import discord
import DataHelper


class HostCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("BotCommands Cog is ready")

    @commands.command()
    async def nice(self, ctx):
        await self.client.player_data.add_player(ctx.author)
        user = ctx.author
        users = await DataHelper.get_player_data()

        visitors_id = users[str(user.id)]["Visited"]

        # When player is not visited
        if visitors_id is False:
            em_no_visit = discord.Embed(color=discord.Color.red())
            em_no_visit.add_field(name="No one came to visit you yet :(",
                                  value="Just wait a little longer...")
            em_no_visit.set_footer(text=f"{ctx.author} tried to give a gift to no one")
            await ctx.author.send(embed=em_no_visit)
            return

        # !nice is DM specific
        # wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Host")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        # when someone actually did visit
        if visitors_id is not False:
            await DataHelper.update_stats(visitors_id, 0, "nice", "Received")
            await DataHelper.update_stats(visitors_id, 0, ctx.author.id, "Giver")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Visited")
            await DataHelper.update_stats(visitors_id, 0, False, "Visiting")
            visitor = await self.client.fetch_user(visitors_id)

            # Getting and delivering a gift is blue
            em_guest = discord.Embed(color=discord.Color.blue())
            em_guest.add_field(name=f"{ctx.author.name} has given you a gift!",
                               value="Unbox, decline or trash it in the server")
            em_guest.set_footer(text=f"{ctx.author} gave a gift to {visitor}")

            await visitor.send(embed=em_guest)

            em_host = discord.Embed(color=discord.Color.green())
            em_host.add_field(name=f"Package given to {visitor.name}",
                              value=f"{visitor.name} may unbox, decline or trash it in the server")
            em_host.set_footer(text=f"{visitor} received a gift from {ctx.author}")

            await ctx.author.send(embed=em_host)

    @commands.command()
    async def devious(self, ctx):
        await self.client.player_data.add_player(ctx.author)
        user = ctx.author
        users = await DataHelper.get_player_data()

        visitor_id = users[str(user.id)]["Visited"]

        # When player is not visited
        if visitor_id is False:
            em_no_visit = discord.Embed(color=discord.Color.red())
            em_no_visit.add_field(name="No one came to visit you yet :(",
                                  value="Just wait a little longer...")
            em_no_visit.set_footer(text=f"{ctx.author} tried to give a gift to no one")
            await ctx.author.send(embed=em_no_visit)
            return

        # wrong chat is brand red
        msg = await self.client.player_data.wrong_chat(ctx.channel.id, ctx.guild, "Host")
        if msg:
            em_wrong_c = discord.Embed(color=discord.Color.brand_red())
            em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
            await ctx.author.send(embed=em_wrong_c)
            return

        if visitor_id is not False:
            await DataHelper.update_stats(visitor_id, 0, "devious", "Received")
            await DataHelper.update_stats(visitor_id, 0, ctx.author.id, "Giver")
            await DataHelper.update_stats(ctx.author.id, 0, False, "Visited")
            await DataHelper.update_stats(visitor_id, 0, False, "Visiting")
            visitor = await self.client.fetch_user(visitor_id)

            # Getting and delivering a gift is blue
            em_guest = discord.Embed(color=discord.Color.blue())
            em_guest.add_field(name=f"{ctx.author.name} has given you a gift!",
                               value="Unbox, decline or trash it in the server")
            em_guest.set_footer(text=f"{ctx.author} gave a gift to {visitor}")

            await visitor.send(embed=em_guest)

            em_host = discord.Embed(color=discord.Color.green())
            em_host.add_field(name=f"Package given to {visitor.name}",
                              value=f"{visitor.name} may unbox, decline or trash it in the server")
            em_host.set_footer(text=f"{visitor} received a gift from {ctx.author}")

            await ctx.author.send(embed=em_host)


async def setup(client):
    await client.add_cog(HostCommands(client))
