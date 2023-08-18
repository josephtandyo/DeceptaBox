from discord.ext import commands
import GetSetStats
import SendEmbed


# STATUS: FINISHED
# cog class for host commands
class HostCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("BotCommands Cog is ready")

    # !nice is a command that sends a nice gift to a visitor
    @commands.command()
    async def nice(self, ctx):
        await self.general_host(ctx, "nice")

    # !devious is a command that sends a devious gift to a visitor
    @commands.command()
    async def devious(self, ctx):
        await self.general_host(ctx, "devious")

    # general_host is a template for the host command since !devious and !nice does the same thing except the gifts
    async def general_host(self, ctx, gift_type):
        author = ctx.author
        channel = ctx.channel
        server = ctx.guild

        # add the author to players.json
        await self.client.leaderboards_handling.add_player(author)

        # check the player that visited author
        visitors_id = await GetSetStats.get_stat(author.id, "Visited")
        # when author has no visitor
        if visitors_id is False:
            await SendEmbed.send_gift_no_one(author)
            return
        # get the player visiting
        player = await self.client.fetch_user(visitors_id)

        # check to see if author and player can be DMs
        if await self.client.player_data.cant_dm_user(channel):
            await SendEmbed.send_cant_dm_author(author)

        if await self.client.player_data.cant_dm_user(player):
            await SendEmbed.send_cant_dm_player(player, channel)



        # check if the command is sent in the server
        # return if sent in the server
        if await self.client.wrong_chat.check_host_wc(author, server):
            return

        # when author has a visitor
        if visitors_id is not False:
            # update the information with the fact that author gave a gift
            await GetSetStats.update_giving_gift_stats(author.id, visitors_id, gift_type)

            # send the message to author and visitor player
            await SendEmbed.send_gift(author, player)


# cog set up
async def setup(client):
    await client.add_cog(HostCommands(client))
