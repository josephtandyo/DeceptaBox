import json
import main


async def add_high_score(user):
    if user == main.client.user:
        return

    score = await get_high_score_data()
    if str(user.id) in score:
        return False
    else:
        score[str(user.id)] = {}
        score[str(user.id)]["New Score"] = 0
        score[str(user.id)]["Old Score"] = 0
        score[str(user.id)]["Deaths"] = 0

    with open("highscores.json", "w") as f:
        json.dump(score, f)

    return True


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


async def make_highscores():
    users = await get_high_score_data()

    player_list = {}
    winner_list = []
    for player_id in users.keys():
        player_list[player_id] = users[str(player_id)]["New Score"]

    sorted_values = sorted(player_list.values())
    sorted_players = {}

    for i in sorted_values:
        for k in player_list.keys():
            if player_list[k] == i:
                sorted_players[k] = player_list[k]

    for player_id in sorted_players:
        winner_list.insert(0, player_id)

    if len(sorted_values) == 0:
        name = "There are No High Scores"
        value = "No one got a high score yet"
        status = ":("
        return [name], [value], [status]

    else:
        name_list = []
        value_list = []
        status_list = []
        for count, winner in enumerate(winner_list, start=1):
            if count == 11:
                return name_list, value_list, status_list
            else:
                player_name = await main.client.fetch_user(int(winner))
                name = str(count) + ". " + str(player_name)
                value = str("High Score: " + str(users[str(winner)]["New Score"]))
                death = str("Deaths: " + str(users[str(winner)]["Deaths"]))

                name_list.append(name)
                value_list.append(value)
                status_list.append(death)

        return name_list, value_list, status_list
