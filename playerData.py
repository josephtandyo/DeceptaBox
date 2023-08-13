import main
import json

async def add_player(user):
    if user == main.client.user:
        return
    users = await get_player_data()
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


async def reset_data():
    with open("players.json", "w") as f:
        f.write("{ \n }")


async def get_player_data():
    with open("players.json", "r") as f:
        users = json.load(f)
    return users


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


async def make_leaderboard(final=False):
    users = await get_player_data()

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
                player_name = await main.client.fetch_user(int(winner))
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