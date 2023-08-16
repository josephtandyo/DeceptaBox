from discord.ext import commands
import SendEmbed
import settings
# STATUS: FINISHED


class WrongChat(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("WrongChat Cog is ready")

    # check basic commands if sent in wrong chat
    async def check_basic_wc(self, author, channel_id, server):
        # get the channel that is desired
        channel = await self.client.fetch_channel(settings.channel_ID)

        # basic commands are in wrong chat if it's the wrong channel, and it's in the server
        if channel_id != settings.channel_ID and server is not None:
            await SendEmbed.send_basic_wc(author, channel)
            return True
        return False

    # check guest commands if sent in wrong chat
    async def check_guest_wc(self, author, channel_id, server):
        channel = await self.client.fetch_channel(settings.channel_ID)

        # guest commands are in wrong chat if it's the wrong channel, and it's not in the server
        if channel_id != settings.channel_ID or server is None:
            await SendEmbed.send_guest_wc(channel, author)
            return True
        return False


# check host commands if sent in wrong chat
async def check_host_wc(author, server):
    # host commands are in wrong chat if it's in the server
    if server is not None:
        await SendEmbed.send_host_wc(author)
        return True
    return False


# cog set up
async def setup(client):
    await client.add_cog(WrongChat(client))
