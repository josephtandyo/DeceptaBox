from discord.ext import commands
import DataHelper
import GetSetStats
import SendEmbed


# STATUS: FINISHED
# cog class for leaderboards
class LeaderboardsHandling(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.sorted_valid_users_id = []

        self.lb_name_list = []
        self.lb_points_list = []
        self.lb_status_list = []
        self.valid_users_dict = {}

    @commands.Cog.listener()
    async def on_start(self):
        print("LeaderboardsHandling Cog is ready")

    # helper method that will get list of IDs in a list that are valid players in order: [373262, 38434231, 347238]
    async def validate_top_ten(self):
        # reset the lists when validating again
        self.sorted_valid_users_id = []
        self.lb_name_list = []
        self.lb_points_list = []
        self.lb_status_list = []

        users = await DataHelper.get_player_data()
        self.valid_users_dict = {}
        counter = 0
        for user_id in users.keys():
            user_point = await GetSetStats.get_stat(user_id, "Total Points")

            # don't include players with no points
            if user_point == 0:
                continue

            # only get the top 10
            elif counter != 10:
                # make a dictionary in the form like: {723832: 4} where the key is the ID and value is total points
                self.valid_users_dict[user_id] = user_point
                counter += 1

        # now sort this dictionary by their total points and save the sorted player IDs
        self.sorted_valid_users_id = sorted(self.valid_users_dict, key=self.valid_users_dict.get, reverse=True)

    # main helper method that will convert the IDs into names and return a list of these names: [user1, user2]
    async def sort_users_stats(self):
        await self.validate_top_ten()

        # for every id in the sorted id list, convert it to a name and append to a name list
        for user_id in self.sorted_valid_users_id:
            user_name = await self.client.fetch_user(user_id)
            self.lb_name_list.append(user_name)

            # get the total points value and append it to a points list
            points = await GetSetStats.get_stat(user_id, "Total Points")
            self.lb_points_list.append(points)

            # get the death status and append it to a status list
            death_status = await GetSetStats.get_stat(user_id, "Dead")
            self.lb_status_list.append("Dead") if death_status else self.lb_status_list.append("Alive")

    # main method that will send the leaderboards message
    async def send_leaderboards(self, channel):
        await self.sort_users_stats()

        # if the name length is 0 then the leaderboards is empty
        if len(self.lb_name_list) == 0:
            # send the empty leaderboards
            await SendEmbed.send_empty_leaderboards(channel)
            return
        # send the leaderboards
        await SendEmbed.send_leaderboards(self.lb_name_list, self.lb_points_list, self.lb_status_list, channel)

    # method to add player to players.json and leaderboards dictionary
    async def add_player(self, user):

        # if the user is the bot itself, return
        if user == self.client.user:
            return

        # get the json file
        users = await DataHelper.get_player_data()

        # if they are already in the json file return
        if str(user.id) in users:
            return False
        else:
            # initialize stats
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

            users[str(user.id)]["List Of Visitors"] = []

        await DataHelper.update_player_data(users)

        return True


# cog setup
async def setup(client):
    await client.add_cog(LeaderboardsHandling(client))
