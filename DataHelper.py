import json


async def get_player_data():
    with open("players.json", "r") as f:
        users = json.load(f)
    return users


async def update_player_data(users):
    with open("players.json", "w") as f:
        json.dump(users, f)


async def reset_player_data():
    with open("players.json", "w") as f:
        f.write("{ \n }")


async def get_highscore_data():
    with open("highscores.json", "r") as f:
        users = json.load(f)
    return users


async def update_highscore_data(users):
    with open("players.json", "w") as f:
        json.dump(users, f)
