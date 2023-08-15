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

    async def make_member(self, player_id):
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

    async def make_leaderboard(self, final=False):
        users = await DataHelper.get_player_data()

        player_list = {}
        winner_list = []
        for player_id in users.keys():
            if users[str(player_id)]["Join"]:
                player_list[player_id] = users[str(player_id)]["Total Points"]

        sorted_values = sorted(player_list.values())
        sorted_players = {}

        for i in sorted_values:
            for k in player_list.keys():
                if player_list[k] == i:
                    sorted_players[k] = player_list[k]

        for player_id in sorted_players:
            winner_list.insert(0, player_id)

        title = ""

        if final is False:
            title = "The Current Leaderboard:"

        elif final is True:
            title = "The Final Leaderboard:"

        if len(sorted_values) == 0:
            name = "The Leaderboard is Empty"
            value = "There are no players playing"
            status = ":("
            return title, [name], [value], [status]

        else:
            name_list = []
            value_list = []
            status_list = []
            for count, winner in enumerate(winner_list, start=1):
                if count == 11:
                    return title, name_list, value_list, status_list
                else:
                    player_name = await self.client.fetch_user(int(winner))
                    name = str(count) + ". " + str(player_name)
                    value = str("Total Points: " + str(users[str(winner)]["Total Points"]))
                    death = users[str(winner)]["Dead"]
                    if death:
                        death = "Dead"
                    elif not death:
                        death = "Alive"
                    status = str("`" + death + "`")
                    name_list.append(name)
                    value_list.append(value)
                    status_list.append(status)

            return title, name_list, value_list, status_list

    async def add_high_score(self, user):
        if user == self.client.user:
            return

        score = await DataHelper.get_high_score_data()
        if str(user.id) in score:
            return False
        else:
            score[str(user.id)] = {}
            score[str(user.id)]["New Score"] = 0
            score[str(user.id)]["Old Score"] = 0
            score[str(user.id)]["Deaths"] = 0

        with open("../highscores.json", "w") as f:
            json.dump(score, f)

        return True

    async def make_highscores(self):
        users = await DataHelper.get_high_score_data()

        player_list = {}
        winner_list = []
        for player_id in users.keys():
            player_list[player_id] = users[str(player_id)]["New Score"]

        sorted_values = sorted(player_list.values())
        sorted_players = {}

        for i in sorted_values:
            for k in player_list.keys():
                if player_list[k] == i:
                    sorted_players[k] = player_list[k]

        for player_id in sorted_players:
            winner_list.insert(0, player_id)

        if len(sorted_values) == 0:
            name = "There are No High Scores"
            value = "No one got a high score yet"
            status = ":("
            return [name], [value], [status]

        else:
            name_list = []
            value_list = []
            status_list = []
            for count, winner in enumerate(winner_list, start=1):
                if count == 11:
                    return name_list, value_list, status_list
                else:
                    player_name = await self.client.fetch_user(int(winner))
                    name = str(count) + ". " + str(player_name)
                    value = str("High Score: " + str(users[str(winner)]["New Score"]))
                    death = str("Deaths: " + str(users[str(winner)]["Deaths"]))

                    name_list.append(name)
                    value_list.append(value)
                    status_list.append(death)

            return name_list, value_list, status_list

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
    await client.add_cog(PlayerData(client))
