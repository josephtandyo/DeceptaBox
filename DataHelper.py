import json

import settings


async def get_high_score_data():
    with open("highscores.json", "r") as f:
        users = json.load(f)
    return users


async def update_high_score(user, add=0, replace=False, mode="High Score"):
    users = await get_high_score_data()
    if replace:
        users[str(user)][mode] = int(add)
    elif not replace and add:
        users[str(user)][mode] += add
    with open("highscores.json", "w") as f:
        json.dump(users, f)

    high_score_info = [users[str(user)]["New Score"],
                       users[str(user)]["Old Score"],
                       users[str(user)]["Deaths"]]
    return high_score_info


async def get_player_data():
    with open("players.json", "r") as f:
        users = json.load(f)
    return users


async def reset_data():
    with open("players.json", "w") as f:
        f.write("{ \n }")


async def update_stats(user, new_points=0, new_status=None, mode="Total Points"):
    users = await get_player_data()
    if new_points:
        users[str(user)][mode] += new_points
    elif new_status or new_status is False:
        users[str(user)][mode] = new_status
    with open("players.json", "w") as f:
        json.dump(users, f)

    stat_info = [users[str(user)]["Total Points"],
                 users[str(user)]["Unboxed Points"],
                 users[str(user)]["Declined Points"],
                 users[str(user)]["Kill Points"],
                 users[str(user)]["Accidental Kill"],
                 users[str(user)]["Trashability"],

                 users[str(user)]["Visited"],
                 users[str(user)]["Received"],
                 users[str(user)]["Visiting"],
                 users[str(user)]["Giver"],
                 users[str(user)]["Dead"],
                 users[str(user)]["Join"]]
    return stat_info


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


async def dead_person(role_id, specifics=None):
    dead_role_id = settings.dead_role_ID
    role_name = settings.dead_role_NAME

    if role_id == dead_role_id and specifics == "visiting dead":
        return "The host you tried to visit have **died**, you would be visiting a haunted house"
    elif role_id == dead_role_id and specifics == "dead visiting":
        return "You have **died** and cannot haunt anyone"
    elif role_id == dead_role_id and specifics == "dead home":
        return "You have **died** and cannot come home"
    elif role_id == dead_role_id and specifics == "dead unboxing":
        return "you have **died** and you cannot unbox any gifts"
    elif role_id == dead_role_id and specifics == "dead declining":
        return "you have **died** and you cannot decline any gifts"
    elif role_id == dead_role_id and specifics == "dead trashing":
        return "you have **died** and you cannot trash any gifts"
    elif role_id == dead_role_id and specifics == "remove role":
        return True, role_name
    elif role_id != dead_role_id and specifics == "remove role":
        return False, role_name
