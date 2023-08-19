import json


# STATUS: FINISHED
# get the json file for player data
async def get_player_data():
    with open("players.json", "r") as f:
        users = json.load(f)
    return users


# update the json file for player data
async def update_player_data(users):
    with open("players.json", "w") as f:
        json.dump(users, f)


# reset the json file for player data (and leaderboards)
async def reset_player_data():
    with open("players.json", "w") as f:
        f.write("{ \n }")


# get the json file for highscore data
async def get_highscore_data():
    with open("highscores.json", "r") as f:
        users = json.load(f)
    return users


# update the json file for highscore data
async def update_highscore_data(users):
    with open("highscores.json", "w") as f:
        json.dump(users, f)
