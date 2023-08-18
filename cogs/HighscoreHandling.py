from discord.ext import commands
import DataHelper
import GetSetHighscores
import SendEmbed


class HighscoreHandling(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.sorted_top_users_id = []
        self.hs_name_list = []
        self.hs_points_list = []
        self.hs_deaths_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("HighscoreHandling Cog is ready")

    async def sort_highscores(self):
        users = await DataHelper.get_highscore_data()
        top_users_dict = {}
        counter = 0
        for user_id in users.keys():
            user_point = await GetSetHighscores.get_score(user_id, "High Score")
            if user_point == 0:
                continue

            # only get the top 10
            elif counter != 10:
                # make a dictionary in the form like: {723832: 4} where the key is the ID and value is total points
                top_users_dict[user_id] = user_point
                counter += 1

        # now sort this dictionary by their total points and save the sorted player IDs
        self.sorted_top_users_id = sorted(top_users_dict, key=top_users_dict.get, reverse=True)

    async def sort_users_hs(self):
        await self.sort_highscores()

        # for every id in the sorted id list, convert it to a name and append to a name list
        for user_id in self.sorted_top_users_id:
            user_name = await self.client.fetch_user(user_id)
            self.hs_name_list.append(user_name)

            # get the total points value and append it to a points list
            points = await GetSetHighscores.get_score(user_id, "High Score")
            self.hs_points_list.append(points)

            # get the death status and append it to a status list
            death_amount = await GetSetHighscores.get_score(user_id, "Deaths")
            self.hs_deaths_list.append(death_amount)

    async def send_highscores(self, channel):
        await self.sort_users_hs()
        # send the leaderboards
        await SendEmbed.send_highscores(self.hs_name_list, self.hs_points_list, self.hs_deaths_list, channel)

    async def add_highscore(self, user):
        if user == self.client.user:
            return

        score = await DataHelper.get_highscore_data()
        if str(user.id) in score:
            return False
        else:
            score[str(user.id)] = {}
            score[str(user.id)]["High Score"] = 0
            score[str(user.id)]["Deaths"] = 0

        await DataHelper.update_highscore_data(score)

        return True


async def setup(client):
    await client.add_cog(HighscoreHandling(client))
