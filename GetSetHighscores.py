import DataHelper
import GetSetStats


# STATUS: FINISHED
# getting specific highscore stats
async def get_score(user_id, score):
    users = await DataHelper.get_highscore_data()
    return users[str(user_id)][score]


# check to see if the highscore needs to be updated, and got new highscore
async def update_highscore(user_id):
    users = await DataHelper.get_highscore_data()
    prev_highscore = users[str(user_id)]["High Score"]
    current_score = await GetSetStats.get_stat(user_id, "Total Points")
    if current_score > prev_highscore:
        users[str(user_id)]["High Score"] = current_score

    await DataHelper.update_highscore_data(users)


# increase the deaths amount by one
async def increase_deaths(user_id):
    users = await DataHelper.get_highscore_data()
    users[str(user_id)]["Deaths"] += 1
    await DataHelper.update_highscore_data(users)
