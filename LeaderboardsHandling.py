import DataHelper
import GetSetStats


async def get_sorted_valid_stats():
    users = await DataHelper.get_player_data()
    valid_users_dict = {}
    counter = 0
    for user_id in users.keys():
        if counter == 10:
            break
        if await GetSetStats.get_stat(user_id, "Join"):
            valid_users_dict[user_id] = await GetSetStats.get_stat(user_id, "Total Points")
            counter += 1

    sorted_valid_users = sorted(valid_users_dict, key=valid_users_dict.get, reverse=True)
    sorted_valid_values = sorted(valid_users_dict.values(), reverse=True)
    sorted_valid_status = []

    for user_id in sorted_valid_users:
        sorted_valid_status.append(await GetSetStats.get_stat(user_id, "Dead"))

    return sorted_valid_users, sorted_valid_values, sorted_valid_status


async def make_leaderboard(final=False):
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
                player_name = (int(winner))
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


# async def get_lb_name_list():
#     return name_list

