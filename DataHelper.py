import json


async def get_player_data():
    with open("players.json", "r") as f:
        users = json.load(f)
    return users


async def reset_data():
    with open("players.json", "w") as f:
        f.write("{ \n }")


async def update_data(users):
    with open("players.json", "w") as f:
        json.dump(users, f)



async def check_winner():
    users = await get_player_data()
    dead_list = []
    if len(users) > 1:
        for user in users:
            if users[str(user)]["Dead"]:
                dead_list.append(1)
            elif not users[str(user)]["Dead"]:
                dead_list.append(0)

    alive = dead_list.count(0)

    if alive == 1:
        return True
