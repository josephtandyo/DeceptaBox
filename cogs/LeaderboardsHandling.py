import asyncio

from discord.ext import commands
import json
import DataHelper
import settings
import discord
import datetime
from discord.utils import get


class LeaderboardsHandling(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.name_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("LeaderboardsHandling Cog is ready")

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

async def get_lb_name_list():
    return name_list

async def setup(client):
    await client.add_cog(LeaderboardsHandling(client))
