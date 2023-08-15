from discord.ext import commands

import SendEmbed
import settings


class DeathHandling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("DeathHandling Cog is ready")

    async def check_death(self, channel, author, player):
        dead_role_id = settings.dead_role_ID

        for role in author.roles:
            if role.id == dead_role_id:
                await SendEmbed.send_author_d(channel, author, player)
                return True

        for role in player.roles:
            if role.id == dead_role_id:
                await SendEmbed.send_player_d(channel, author, player)
                return True
        return False


async def dead_person(role_id, specifics=None):
    dead_role_id = settings.dead_role_ID
    role_name = settings.dead_role_NAME

    if role_id == dead_role_id and specifics == "remove role":
        return True, role_name
    elif role_id != dead_role_id and specifics == "remove role":
        return False, role_name


async def setup(client):
    await client.add_cog(DeathHandling(client))
