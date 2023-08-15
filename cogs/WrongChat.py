from discord.ext import commands

import SendEmbed
import settings


class WrongChat(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("WrongChat Cog is ready")

    # check
    async def check_basic_wc(self, channel_id, in_server, author):
        channel = await self.client.fetch_channel(settings.channel_ID)

        # when wrong channel and not in dm
        if channel_id != settings.channel_ID and in_server is not None:
            await SendEmbed.send_basic_wc(channel, author)
            return True

        return False

    async def check_guest_wc(self, channel_id, in_server, author):
        channel = await self.client.fetch_channel(settings.channel_ID)

        if channel_id != settings.channel_ID or in_server is None:
            await SendEmbed.send_guest_wc(channel, author)
            return True
        return False


 # TODO delete below
    async def wrong_chat(self, channel_id, in_server, command_type):
        desired_channel_id = settings.channel_ID

        channel = await self.client.fetch_channel(desired_channel_id)

        # when wrong channel and not in dm
        if channel_id != desired_channel_id and in_server is not None and command_type == "Basic":
            return f"You can't use this command in this channel, only in **#{channel}** or in **DM with the bot**"

        # when wrong channel or in dm
        elif (channel_id != desired_channel_id or in_server is None) and command_type == "Guest":
            return f"You can't use this command in this channel or in the DM with the bot, only in **#{channel}**"

        # when not in dm
        elif channel_id == desired_channel_id and in_server is not None and command_type == "Host":
            return "Oops, you should use this command only in **DM with the bot** to keep the gift contents a secret"

        elif channel_id != desired_channel_id and in_server is not None and command_type == "Host":
            return f"You can't use this command in this channel, only in **DM with the bot**"


async def setup(client):
    await client.add_cog(WrongChat(client))
