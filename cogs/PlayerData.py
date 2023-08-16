import asyncio

from discord.ext import commands
import json
import DataHelper
import settings
import discord
import datetime
from discord.utils import get


class PlayerData(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("PlayerData Cog is ready")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em_tired = discord.Embed(color=discord.Color.yellow())
            minutes = int(error.retry_after / 60)
            rounded = (error.retry_after / 60) - minutes
            seconds = int(rounded * 60)
            em_tired.add_field(name=f"You can't visit anyone for **{minutes} minutes** and **{seconds} seconds**",
                               value="This is because you are tired after the last visit")
            em_tired.set_footer(text="To check how much time until the next visit, visit the bot in the DM")
            await ctx.channel.send(embed=em_tired)

    async def convert_to_obj(self, player_id):
        guild_id = settings.guild_ID

        guild_obj = self.client.get_guild(guild_id)
        member_obj = guild_obj.get_member(int(player_id))

        return member_obj

    async def add_player(self, user):
        if user == self.client.user:
            return
        users = await DataHelper.get_player_data()
        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["Total Points"] = 0
            users[str(user.id)]["Unboxed Points"] = 0
            users[str(user.id)]["Declined Points"] = 0
            users[str(user.id)]["Kill Points"] = 0
            users[str(user.id)]["Accidental Kill"] = 0
            users[str(user.id)]["Trashability"] = 0

            users[str(user.id)]["Visited"] = False
            users[str(user.id)]["Received"] = False
            users[str(user.id)]["Visiting"] = False
            users[str(user.id)]["Giver"] = False
            users[str(user.id)]["Dead"] = False
            users[str(user.id)]["Join"] = False

        with open("players.json", "w") as f:
            json.dump(users, f)

        return True

    async def reset(self):
        channel_id = settings.channel_ID
        guid_id = settings.guild_ID

        # change time
        while True:
            now = datetime.datetime.now()
            then = now + datetime.timedelta(minutes=5)
            then.replace(hour=0, minute=1)
            wait_time = (then - now).total_seconds()
            await asyncio.sleep(wait_time)

            channel = self.client.get_channel(channel_id)
            guild = self.client.get_guild(guid_id)

            # final leaderboard is dark gold
            title, name_list, value_list, status = await self.make_leaderboard(True)
            em_board = discord.Embed(title=title, color=discord.Color.orange())
            if name_list == ['The Leaderboard is Empty']:
                print("No one played today")

            else:
                for num in range(len(name_list)):
                    em_board.add_field(name=name_list[num],
                                       value=value_list[num] + " \n" + status[num])

                first_name = name_list[0]
                first_score = value_list[0]

                # winner announcement is gold
                em_announce = discord.Embed(color=discord.Color.gold())
                em_announce.add_field(name=f"The day is over! **{first_name[3:]} WINS!!**",
                                      value=f"With a final score of {first_score[13:]}")
                em_announce.set_footer(text=f"The leaderboard is reset, and everyone came back to life")
                await channel.send(embed=em_announce)
                await channel.send(embed=em_board)

                users = await DataHelper.get_player_data()
                for player_id in users.keys():
                    member_obj = await self.make_member(player_id)
                    for roles in member_obj.roles:
                        remove_role, role_name = await DataHelper.dead_person(roles.id, "remove role")
                        if remove_role:
                            dead_role = get(guild.roles, name=role_name)
                            await member_obj.remove_roles(dead_role)
                await DataHelper.reset_data()

                scores = await DataHelper.get_high_score_data()
                for user_id in scores.keys():
                    await DataHelper.update_high_score(user_id, 0, True, "Old Score")
                # client.get_command("visit").reset_cooldown(ctx)


async def setup(client):
    await client.add_cog(PlayerData(client))
