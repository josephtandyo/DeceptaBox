from discord.ext import commands
import DataHelper
import GetSetHighscores
import SendEmbed


# STATUS: FINISHED
# cog class for handling highscores
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

    # method that sorts the highscores from high to low
    async def sort_highscores(self):
        self.sorted_top_users_id = []
        self.hs_name_list = []
        self.hs_points_list = []
        self.hs_deaths_list = []

        users = await DataHelper.get_highscore_data()
        top_users_dict = {}
        counter = 0
        for user_id in users.keys():
            user_point = await GetSetHighscores.get_score(user_id, "High Score")

            # if their highscore is 0, don't include them in the top scores
            if user_point == 0:
                continue

            # only get the top 10 for the highscore
            elif counter != 10:
                # make a dictionary in the form like: {723832: 4} where the key is the ID and value is highscore
                top_users_dict[user_id] = user_point
                counter += 1

        # now sort this dictionary by their highscore and save the sorted player IDs
        self.sorted_top_users_id = sorted(top_users_dict, key=top_users_dict.get, reverse=True)

    # sort the highscores by appending to lists
    async def sort_users_hs(self):
        await self.sort_highscores()

        # for every id in the sorted id list, convert it to a name and append to a name list
        for user_id in self.sorted_top_users_id:
            # get the names of the top players and append to the name list
            user_name = await self.client.fetch_user(user_id)
            self.hs_name_list.append(user_name)

            # get the total points value and append it to a hs points list
            points = await GetSetHighscores.get_score(user_id, "High Score")
            self.hs_points_list.append(points)

            # get the deaths amount and append it to the deaths list
            death_amount = await GetSetHighscores.get_score(user_id, "Deaths")
            self.hs_deaths_list.append(death_amount)

    # send the highscore message
    async def send_highscores(self, channel):
        await self.sort_users_hs()
        # send the leaderboards
        await SendEmbed.send_highscores(self.hs_name_list, self.hs_points_list, self.hs_deaths_list, channel)

    # add user to the highscores json file
    async def add_highscore(self, user):

        # if they are the bot, return
        if user == self.client.user:
            return

        # get the json file dictionary
        score = await DataHelper.get_highscore_data()

        # if they are already in it, return
        if str(user.id) in score:
            return False
        else:
            score[str(user.id)] = {}
            score[str(user.id)]["High Score"] = 0
            score[str(user.id)]["Deaths"] = 0

        await DataHelper.update_highscore_data(score)

        return True


# cog set up
async def setup(client):
    await client.add_cog(HighscoreHandling(client))
