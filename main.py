import asyncio
import datetime
import shutil

import discord
import os
from discord.ext import commands
from discord.utils import get
import psutil

import settings
import tokens

import highscores
import playerData

# hardcode: [channel specific, role specific, server specific]
# VERSION 1.5
# Added high score and reset score everyday

os.chdir(settings.file_location)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)


@client.event
async def on_ready():
    print("Ready")

    # CPU usage
    print('The CPU usage is:',
          psutil.cpu_percent(interval=1))  # Use interval to specify the time interval for CPU usage measurement

    # Memory usage
    memory = psutil.virtual_memory()
    print('RAM memory % used:', memory.percent)
    print('RAM Used (GB):', memory.used / 1e9)  # Divide by 1e9 to convert bytes to GB

    # Disk space
    path = "C:/Users/josep/PycharmProjects/General Discord Bot"
    stat = shutil.disk_usage(path)
    print("Disk usage statistics:")
    print('Total:', stat.total / 1e9, 'GB')  # Convert bytes to GB for total space
    print('Used:', stat.used / 1e9, 'GB')  # Convert bytes to GB for used space
    print('Free:', stat.free / 1e9, 'GB')  # Convert bytes to GB for free space

    # Network bandwidth (requires additional libraries or APIs)

    await reset()


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em_tired = discord.Embed(color=discord.Color.yellow())
        minutes = int(error.retry_after / 60)
        rounded = (error.retry_after / 60) - minutes
        seconds = int(rounded * 60)
        em_tired.add_field(name=f"You can't visit anyone for **{minutes} minutes** and **{seconds} seconds**",
                           value="This is because you are tired after the last visit")
        em_tired.set_footer(text="To check how much time until the next visit, visit the bot in the DM")
        await ctx.channel.send(embed=em_tired)


async def wrong_chat(channel_id, in_server, command_type):
    desired_channel_id = settings.channel_ID

    channel = await client.fetch_channel(desired_channel_id)
    # when wrong channel and not in dm
    if channel_id != desired_channel_id and in_server is not None and command_type == "Basic":
        return f"You can't use this command in this channel, only in **#{channel}** or in **DM with the bot**"

    # when wrong channel or in dm
    elif (channel_id != desired_channel_id or in_server is None) and command_type == "Guest":
        return f"You can't use this command in this channel or in the DM with the bot, only in **#{channel}**"

    # when not in dm
    elif channel_id == desired_channel_id and in_server is not None and command_type == "Host":
        return "Oops, you should use this command only in the **DM with the bot** to keep the gift contents a secret"

    elif channel_id != desired_channel_id and in_server is not None and command_type == "Host":
        return f"You can't use this command in this channel, only in **DM with the bot**"


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


async def make_member(player_id):
    guild_id = settings.guild_ID

    guild_obj = client.get_guild(guild_id)
    member_obj = guild_obj.get_member(int(player_id))

    return member_obj


async def reset():
    channel_id = settings.channel_ID
    guid_id = settings.guild_ID

    #change time
    while True:
        now = datetime.datetime.now()
        then = now + datetime.timedelta(minutes=5)
        then.replace(hour=0, minute=1)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        channel = client.get_channel(channel_id)
        guild = client.get_guild(guid_id)

        # final leaderboard is dark gold
        title, name_list, value_list, status = await playerData.make_leaderboard(True)
        em_board = discord.Embed(title=title, color=discord.Color.orange())
        if name_list == ['The Leaderboard is Empty']:
            print("No one played today")

        else:
            for num in range(len(name_list)):
                em_board.add_field(name=name_list[num],
                                   value=value_list[num] + " \n" + status[num])

            first_name = name_list[0]
            first_score = value_list[0]

            # winner announcement is gold
            em_announce = discord.Embed(color=discord.Color.gold())
            em_announce.add_field(name=f"The day is over! **{first_name[3:]} WINS!!**",
                                  value=f"With a final score of {first_score[13:]}")
            em_announce.set_footer(text=f"The leaderboard is reset, and everyone came back to life")
            await channel.send(embed=em_announce)
            await channel.send(embed=em_board)

            users = await playerData.get_player_data()
            for player_id in users.keys():
                member_obj = await make_member(player_id)
                for roles in member_obj.roles:
                    remove_role, role_name = await dead_person(roles.id, "remove role")
                    if remove_role:
                        dead_role = get(guild.roles, name=role_name)
                        await member_obj.remove_roles(dead_role)
            await playerData.reset_data()

            scores = await highscores.get_high_score_data()
            for user_id in scores.keys():
                await highscores.update_high_score(user_id, 0, True, "Old Score")
            # client.get_command("visit").reset_cooldown(ctx)


@client.command()
async def rules(ctx):
    # !rules are channel specific and in DM of bot
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Basic")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # Rules and commands are og_blurple
    em_rules = discord.Embed(title="Here are the Basic Rules:", color=discord.Color.og_blurple())
    em_rules.add_field(name="The Main Goal is to Earn as Many Points as Possible Without Dying!",
                       value="\n" #how many minutes
                             "\n**1.** Every idk minutes, you may **visit** other players and act as the guest\n"
                             "\n**2.** The player you visited will act as the host\n"
                             "\n**3.** The host will have the option to give the guest a **nice** gift or a "
                             "**devious** gift\n "
                             "> *The guest can go back **home** if the host hasn't given them a gift yet*\n"
                             "\n**4.** After receiving a gift, the guest can **unbox**, **decline** or **trash** the "
                             "gift "
                             "\n> Unboxing a **nice gift**: The guest will gain **1 point** and **1 trashability**"
                             "\n> Unboxing a **devious gift**: The guest will **DIE** and the host will gain **1 "
                             "point**\n> "
                             "\n> Declining a **nice gift**: The host will gain **1 point**"
                             "\n> Declining a **devious gift**: The host will **DIE** and the guest will gain **1 "
                             "point**\n> "
                             "\n> Thrashing **ANY gift**: The gift is forever **GONE**; the gift type will be revealed"
                             "\n>> *Trashing a gift will use up **1 trashability***\n "
                             "\n**5.** If a player visits you, they will act as the guest and you will act as the "
                             "host\n")
    em_rules.set_footer(text="You can only visit and get visited by one player at a time\n"
                             "You can't visit anyone while a gift has not been unboxed, declined or trashed\n"
                             ">> For the list of commands, type `!guide`")

    await ctx.channel.send(embed=em_rules)


@client.command()
async def guide(ctx):
    # !guide are channel specific and in DM of bot
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Basic")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # Rules and commands are og_blurple
    em_commands = discord.Embed(title="Commands Guide", color=discord.Color.blurple())
    em_commands.add_field(name="Basic Commands:",
                          value="*Use in the Server and DM*\n\n"
                                "**`!guide`**\n"
                                "To see the commands\n\n"
                                "**`!rules`**\n"
                                "To see the rules\n\n"
                                "**`!stats (@...)`**\n"
                                "To see points and \n"
                                "trashability\n\n"
                                "**`!leaderboards`**\n"
                                "To see the current \n"
                                "leaderboard\n\n"
                                "**`!highscores`**\n"
                                "To see the current \n"
                                "high scores")
    em_commands.add_field(name="Guest Commands:",
                          value="*Use in the Server*\n\n"
                                "**`!visit @...`**\n"
                                "To visit other players\n\n"
                                "**`!home`**\n"
                                "To go back home\n\n"
                                "**`!unbox`**\n"
                                "To unbox the gift\n\n"
                                "**`!decline`**\n"
                                "To decline the gift\n\n"
                                "**`!trash`**\n"
                                "To trash the gift")
    em_commands.add_field(name="Host Commands:",
                          value="*Use in the DM*\n\n"
                                "**`!devious`**\n"
                                "To give a devious gift\n\n"
                                "**`!nice`**\n"
                                "To give a nice gift\n\n")

    await ctx.channel.send(embed=em_commands)


# update stats
@client.command()
async def stats(ctx, member: discord.Member = None):
    # !stats are channel specific and in DM of bot
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Basic")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # Checking stats of bot is purple
    if member == client.user:
        em_bot_stat = discord.Embed(title="Present Delivery Bot's Stats", color=discord.Color.purple())
        em_bot_stat.add_field(name="Total Points", value=999)
        em_bot_stat.set_footer(text=f"Requested by: {ctx.author}")
        await ctx.send(embed=em_bot_stat)
        return

    # Checking own stats is magenta
    elif member is None or member == ctx.author:
        await playerData.add_player(ctx.author)
        user = ctx.author
        users = await playerData.get_player_data()

    # Checking other player's stats is dark magenta
    else:
        await playerData.add_player(member)
        user = member
        users = await playerData.get_player_data()

    total = users[str(user.id)]["Total Points"]
    trashability = users[str(user.id)]["Trashability"]
    nice_amt = users[str(user.id)]["Unboxed Points"]
    decline_amt = users[str(user.id)]["Declined Points"]
    kills_amt = users[str(user.id)]["Kill Points"]
    accident_amt = users[str(user.id)]["Accidental Kill"]

    em_stat = discord.Embed(title=f"{user}'s Stats", color=discord.Color.teal())
    em_stat.add_field(name="General Stats",
                      value="*Overall*\n\n"
                            "**Total Points:**\n"
                            f"{total}\n\n"
                            "**Trashability:**\n"
                            f"{trashability}", inline=True)
    em_stat.add_field(name="Guest Stats",
                      value="*Points Gained as a Guest*\n\n"
                            "**Opened Gift Points:**\n"
                            f"{nice_amt}\n\n"
                            "**Killing Hosts Points:**\n"
                            f"{accident_amt}", inline=True)

    em_stat.add_field(name="Host Stats",
                      value="*Points Gained as a Host*\n\n"
                            "**Returned Gift Points:**\n"
                            f"{decline_amt}\n\n"
                            "**Killing Guests Points:**\n"
                            f"{kills_amt}", inline=True)

    em_stat.set_footer(text=f"Requested by: {ctx.author}")
    await ctx.send(embed=em_stat)


@client.command()
async def leaderboards(ctx):
    # channel specific and wrong chat color is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Basic")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # current leaderboard is dark gold
    title, name_list, value_list, status = await playerData.make_leaderboard()

    em_board = discord.Embed(title=title, color=discord.Color.orange())

    for num in range(len(name_list)):
        em_board.add_field(name=name_list[num],
                           value=value_list[num] + " \n" + status[num])

    await ctx.channel.send(embed=em_board)


@client.command()
async def highscores(ctx):
    # channel specific and wrong chat color is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Basic")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # current leaderboard is dark gold
    name_list, value_list, death_list = await highscores.make_highscores()

    em_board = discord.Embed(title="The Current High Scores: ", color=discord.Color.orange())

    for num in range(len(name_list)):
        em_board.add_field(name=name_list[num],
                           value=value_list[num] + " \n" + death_list[num])

    await ctx.channel.send(embed=em_board)


#change the timer
@client.command(cooldown_after_parsing=True)
@commands.cooldown(1, 0, commands.BucketType.user)
async def visit(ctx, member: discord.Member):
    # !visit is server specific command
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Guest")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        client.get_command("visit").reset_cooldown(ctx)
        return

    # Visiting bot is purple
    elif member == client.user:
        em_bot_visit = discord.Embed(color=discord.Color.purple())
        em_bot_visit.add_field(name="Thanks for coming, I have nothing for you though. Try visiting **players**",
                               value="I will teleport you back to where you were")
        em_bot_visit.set_footer(text=f"{ctx.author} arrived at {client.user}'s home")
        await ctx.author.send(embed=em_bot_visit)
        client.get_command("visit").reset_cooldown(ctx)
        return

    await playerData.add_player(ctx.author)
    await playerData.add_player(member)

    # Checking if player is dead. Role specific.
    for role in ctx.author.roles:
        dead_visiting = await dead_person(role.id, "dead visiting")
        if dead_visiting:
            em_dead_a = discord.Embed(color=discord.Color.red())
            em_dead_a.add_field(name="R.I.P", value=dead_visiting, inline=True)
            em_dead_a.set_footer(text=f"{ctx.author} tried to visit {member}")
            await ctx.channel.send(embed=em_dead_a)
            client.get_command("visit").reset_cooldown(ctx)
            return

    # Checking if player visiting is dead. Role specific.
    for role in member.roles:
        visiting_dead = await dead_person(role.id, "visiting dead")
        if visiting_dead:
            em_dead_m = discord.Embed(color=discord.Color.red())
            em_dead_m.add_field(name="R.I.P", value=visiting_dead, inline=True)
            em_dead_m.set_footer(text=f"{ctx.author} tried to visit {member}")
            await ctx.channel.send(embed=em_dead_m)
            client.get_command("visit").reset_cooldown(ctx)
            return

    # Visiting yourself is dark green
    if member == ctx.author:
        em_self = discord.Embed(color=discord.Color.red())
        em_self.add_field(name="You can't visit yourself!",
                          value="How is that possible??")
        em_self.set_footer(text=f"{ctx.author} tried to visit themselves")
        await ctx.channel.send(embed=em_self)
        client.get_command("visit").reset_cooldown(ctx)
        return

    # Visiting no one is dark green
    elif member is None:
        em_none = discord.Embed(color=discord.Color.red())
        em_none.add_field(name="You have not specified who you are visiting!",
                          value="To visit a host, type the command and mention the player you want to visit")
        em_none.set_footer(text=f"{ctx.author} tried to visit no one")
        await ctx.channel.send(embed=em_none)
        client.get_command("visit").reset_cooldown(ctx)
        return

    users = await playerData.get_player_data()
    inventory_full = users[str(ctx.author.id)]["Received"]
    already_visiting = users[str(ctx.author.id)]["Visiting"]
    guest_at_home = users[str(ctx.author.id)]["Visited"]
    guest_at_host = users[str(member.id)]["Visited"]
    not_home = users[str(member.id)]["Visiting"]

    # When the player is already at someone else's house, the color is dark green
    if already_visiting:
        user_visiting = await client.fetch_user(already_visiting)
        if member != user_visiting:
            em_else = discord.Embed(color=discord.Color.red())
            em_else.add_field(name=f"You are already at {user_visiting.name}'s house!",
                              value=f"If you want to visit {member.name} instead, you need to go home first")
            em_else.set_footer(text=f"{ctx.author} tried to visit {member}")
            await ctx.channel.send(embed=em_else)
            client.get_command("visit").reset_cooldown(ctx)
            return

        elif member == user_visiting:
            em_here = discord.Embed(color=discord.Color.red())
            em_here.add_field(name=f"You have arrived at {user_visiting.name}'s house a long time ago!",
                              value=f"Wait for {user_visiting.name} to pick a gift for you, or if you don't want to "
                                    f"wait, "
                                    f"go home")
            em_here.set_footer(text=f"{ctx.author} tried to visit {user_visiting}")
            await ctx.channel.send(embed=em_here)
            client.get_command("visit").reset_cooldown(ctx)
            return

    # When a player is already at their house, the color is dark green
    elif guest_at_host:
        guest_inside = await client.fetch_user(guest_at_host)
        em_full = discord.Embed(color=discord.Color.red())
        em_full.add_field(name=f"{member.name}'s house is full, as {guest_inside.name} is already there!",
                          value=f"Visit {member.name} at a later time or visit somebody else")
        em_full.set_footer(text=f"{ctx.author} tried to visit {member}")
        await ctx.channel.send(embed=em_full)
        client.get_command("visit").reset_cooldown(ctx)
        return

    elif guest_at_home:
        guest_inside = await client.fetch_user(guest_at_home)
        em_leave = discord.Embed(color=discord.Color.red())
        em_leave.add_field(name=f"{guest_inside.name} is at your house!",
                           value=f"Give {guest_inside.name} a gift first before you are able to visit {member.name}")
        em_leave.set_footer(text=f"{ctx.author} tried to visit {member}")
        await ctx.channel.send(embed=em_leave)
        client.get_command("visit").reset_cooldown(ctx)
        return

    elif not_home:
        host_elsewhere = await client.fetch_user(not_home)
        em_empty = discord.Embed(color=discord.Color.red())
        em_empty.add_field(name=f"{member.name} is at {host_elsewhere.name}'s house!",
                           value=f"Wait for {member.name} to return home before visiting {member.name}")
        em_empty.set_footer(text=f"{ctx.author} tried to visit {member}")
        await ctx.channel.send(embed=em_empty)
        client.get_command("visit").reset_cooldown(ctx)
        return

    # When you still have a gift in inventory, the color is dark green
    elif inventory_full:
        em_gift = discord.Embed(color=discord.Color.red())
        em_gift.add_field(name="Your inventory is full!",
                          value=f"Unbox, decline or trash the previous gift before visiting {member.name}")
        em_gift.set_footer(text=f"{ctx.author} tried to visit {member}")
        await ctx.channel.send(embed=em_gift)
        client.get_command("visit").reset_cooldown(ctx)
        return

    # Visiting a valid player is green
    else:
        await playerData.update_stats(member.id, 0, ctx.author.id, "Visited")
        await playerData.update_stats(ctx.author.id, 0, member.id, "Visiting")

        em_host = discord.Embed(color=discord.Color.blue())
        em_host.add_field(name=f"{ctx.author.name} has come to visit!",
                          value=f"Choose a `!nice` or a `!devious` gift for {ctx.author.name}")
        em_host.set_footer(text=f"{ctx.author} arrived at {member}'s home")
        await member.send(embed=em_host)

        em_guest = discord.Embed(color=discord.Color.green())
        em_guest.add_field(name=f"You have arrived!",
                           value=f"Now wait as {member.name} will pick the perfect gift for you...")
        em_guest.set_footer(text=f"{ctx.author} is waiting for a gift at {member}'s home")
        await ctx.channel.send(embed=em_guest)


@client.command()
async def home(ctx):
    # !visit is server specific command
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Guest")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # Checking if player is dead. Role specific.
    for role in ctx.author.roles:
        dead_visiting = await dead_person(role.id, "dead home")
        if dead_visiting:
            em_dead = discord.Embed(color=discord.Color.red())
            em_dead.add_field(name="R.I.P", value=dead_visiting, inline=True)
            em_dead.set_footer(text=f"{ctx.author} tried to go home")
            await ctx.channel.send(embed=em_dead)
            client.get_command("visit").reset_cooldown(ctx)
            return

    await playerData.add_player(ctx.author)
    users = await playerData.get_player_data()
    gift_type = users[str(ctx.author.id)]["Received"]
    already_visiting = users[str(ctx.author.id)]["Visiting"]

    # When the player is home, the color is dark green
    if not already_visiting:
        em_home = discord.Embed(color=discord.Color.red())
        em_home.add_field(name="You are already home!",
                          value="Visit someone first and then you can decide to go home")
        em_home.set_footer(text=f"{ctx.author} tried to go home")
        await ctx.channel.send(embed=em_home)
        return

    # When you have a gift in inventory, the color is dark green
    elif gift_type:
        em_gift = discord.Embed(color=discord.Color.red())
        em_gift.add_field(name="The host has given you a gift already!",
                          value="You cannot leave their house until you unbox, decline or trash the gift")
        em_gift.set_footer(text=f"{ctx.author} tried to go home")
        await ctx.channel.send(embed=em_gift)
        return

    # Able to leave
    else:
        for player_id in users.keys():
            if int(player_id) == int(users[str(ctx.author.id)]["Visiting"]):
                member_obj = await make_member(int(player_id))
                await playerData.update_stats(ctx.author.id, 0, False, "Visiting")
                await playerData.update_stats(member_obj.id, 0, False, "Visited")

                em_host = discord.Embed(color=discord.Color.blue())
                em_host.add_field(name=f"{ctx.author.name} has went home :(",
                                  value=f"You took too long to give them a gift, "
                                        f"{ctx.author.name} got tired of waiting")
                em_host.set_footer(text=f"{ctx.author} went home")
                await member_obj.send(embed=em_host)

                em_guest = discord.Embed(color=discord.Color.green())
                em_guest.add_field(name=f"You have arrived home from {member_obj.name}'s house",
                                   value=f"You can visit a host")
                em_guest.set_footer(text=f"{ctx.author} went home")
                await ctx.channel.send(embed=em_guest)
                client.get_command("visit").reset_cooldown(ctx)


@client.command()
async def nice(ctx):
    await playerData.add_player(ctx.author)
    user = ctx.author
    users = await playerData.get_player_data()

    visitors_id = users[str(user.id)]["Visited"]

    # When player is not visited
    if visitors_id is False:
        em_no_visit = discord.Embed(color=discord.Color.red())
        em_no_visit.add_field(name="No one came to visit you yet :(",
                              value="Just wait a little longer...")
        em_no_visit.set_footer(text=f"{ctx.author} tried to give a gift to no one")
        await ctx.author.send(embed=em_no_visit)
        return

    # !nice is DM specific
    # wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Host")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # when someone actually did visit
    if visitors_id is not False:
        await playerData.update_stats(visitors_id, 0, "nice", "Received")
        await playerData.update_stats(visitors_id, 0, ctx.author.id, "Giver")
        await playerData.update_stats(ctx.author.id, 0, False, "Visited")
        await playerData.update_stats(visitors_id, 0, False, "Visiting")
        visitor = await client.fetch_user(visitors_id)

        # Getting and delivering a gift is blue
        em_guest = discord.Embed(color=discord.Color.blue())
        em_guest.add_field(name=f"{ctx.author.name} has given you a gift!",
                           value="Unbox, decline or trash it in the server")
        em_guest.set_footer(text=f"{ctx.author} gave a gift to {visitor}")

        await visitor.send(embed=em_guest)

        em_host = discord.Embed(color=discord.Color.green())
        em_host.add_field(name=f"Package given to {visitor.name}",
                          value=f"{visitor.name} may unbox, decline or trash it in the server")
        em_host.set_footer(text=f"{visitor} received a gift from {ctx.author}")

        await ctx.author.send(embed=em_host)


@client.command()
async def devious(ctx):
    await playerData.add_player(ctx.author)
    user = ctx.author
    users = await playerData.get_player_data()

    visitor_id = users[str(user.id)]["Visited"]

    # When player is not visited
    if visitor_id is False:
        em_no_visit = discord.Embed(color=discord.Color.red())
        em_no_visit.add_field(name="No one came to visit you yet :(",
                              value="Just wait a little longer...")
        em_no_visit.set_footer(text=f"{ctx.author} tried to give a gift to no one")
        await ctx.author.send(embed=em_no_visit)
        return

    # wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Host")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    if visitor_id is not False:
        await playerData.update_stats(visitor_id, 0, "devious", "Received")
        await playerData.update_stats(visitor_id, 0, ctx.author.id, "Giver")
        await playerData.update_stats(ctx.author.id, 0, False, "Visited")
        await playerData.update_stats(visitor_id, 0, False, "Visiting")
        visitor = await client.fetch_user(visitor_id)

        # Getting and delivering a gift is blue
        em_guest = discord.Embed(color=discord.Color.blue())
        em_guest.add_field(name=f"{ctx.author.name} has given you a gift!",
                           value="Unbox, decline or trash it in the server")
        em_guest.set_footer(text=f"{ctx.author} gave a gift to {visitor}")

        await visitor.send(embed=em_guest)

        em_host = discord.Embed(color=discord.Color.green())
        em_host.add_field(name=f"Package given to {visitor.name}",
                          value=f"{visitor.name} may unbox, decline or trash it in the server")
        em_host.set_footer(text=f"{visitor} received a gift from {ctx.author}")

        await ctx.author.send(embed=em_host)


@client.command()
async def unbox(ctx):
    # !unbox is server specific command
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Guest")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # Checking if player is dead. Role specific.
    for role in ctx.author.roles:
        dead_unboxing = await dead_person(role.id, "dead unboxing")
        if dead_unboxing:
            em_dead = discord.Embed(color=discord.Color.red())
            em_dead.add_field(name="R.I.P", value=dead_unboxing, inline=True)
            em_dead.set_footer(text=f"{ctx.author} tried to unbox a gift")
            await ctx.channel.send(embed=em_dead)
            return

    await playerData.add_player(ctx.author)
    user = ctx.author
    users = await playerData.get_player_data()
    gift_type = users[str(user.id)]["Received"]
    giver_id = users[str(user.id)]["Giver"]

    if gift_type == "nice" and giver_id is not False:
        await playerData.update_stats(ctx.author.id, 1, False, "Total Points")
        await playerData.update_stats(ctx.author.id, 1, False, "Unboxed Points")
        await playerData.update_stats(ctx.author.id, 1, False, "Trashability")
        await playerData.update_stats(ctx.author.id, 0, False, "Received")
        await playerData.update_stats(ctx.author.id, 0, False, "Giver")
        await playerData.update_stats(ctx.author.id, 0, True, "Join")
        await playerData.update_stats(giver_id, 0, True, "Join")

        # earning a point is fuchsia
        em_unbox = discord.Embed(color=discord.Color.fuchsia())
        em_unbox.add_field(name=f"**{ctx.author.name}** unboxed a **nice gift!**",
                           value=f"**{ctx.author.name}** receives **1 point** and **1 trashability**")
        em_unbox.set_footer(text=f"{ctx.author} unboxed a gift")
        await ctx.channel.send(embed=em_unbox)
        giver = await client.fetch_user(giver_id)

        await highscores.add_high_score(ctx.author)
        await highscores.add_high_score(giver)
        await highscores.update_high_score(ctx.author.id, 1, False, "Old Score")
        scores = await highscores.get_high_score_data()

        if int(scores[str(ctx.author.id)]["Old Score"]) > int(scores[str(ctx.author.id)]["New Score"]):
            old_score = int(scores[str(ctx.author.id)]["Old Score"])

            await highscores.update_high_score(ctx.author.id, old_score, True, "New Score")

        return

    elif gift_type == "devious" and giver_id is not False:
        giver = await client.fetch_user(giver_id)
        await playerData.update_stats(giver_id, 1, False, "Total Points")
        await playerData.update_stats(giver_id, 1, False, "Kill Points")
        await playerData.update_stats(ctx.author.id, 0, False, "Received")
        await playerData.update_stats(ctx.author.id, 0, False, "Giver")
        await playerData.update_stats(ctx.author.id, 0, True, "Dead")
        await playerData.update_stats(ctx.author.id, 0, True, "Join")
        await playerData.update_stats(giver_id, 0, True, "Join")

        em_bomb = discord.Embed(color=discord.Color.default())
        em_bomb.add_field(name=f"**{ctx.author.name}** unboxed an explosive **devious gift** and **dies!**",
                          value=f"**{giver.name}** receives **1 point**")
        em_bomb.set_footer(text=f"{ctx.author} unboxed a gift")
        await ctx.channel.send(embed=em_bomb)

        dead_role = get(ctx.guild.roles, name="Dead")
        await ctx.author.add_roles(dead_role)

        await highscores.add_high_score(ctx.author)
        await highscores.add_high_score(giver)
        await highscores.update_high_score(giver.id, 1, False, "Old Score")
        await highscores.update_high_score(ctx.author.id, 1, False, "Deaths")
        scores = await highscores.get_high_score_data()
        if int(scores[str(giver.id)]["Old Score"]) > int(scores[str(giver.id)]["New Score"]):
            await highscores.update_high_score(giver.id, int(scores[str(giver.id)]["Old Score"]), True, "New Score")

        win = await playerData.check_winner()
        if win:
            # final leaderboard is dark gold
            # title, name_list, value_list, status = await make_leaderboard(True)
            # em_board = discord.Embed(title=title, color=discord.Color.orange())
            # for num in range(len(name_list)):
            #     em_board.add_field(name=name_list[num],
            #                        value=value_list[num] + " \n" + status[num])
            # first_name = name_list[0]
            # first_score = value_list[0]
            # # winner announcement is gold
            # em_announce = discord.Embed(color=discord.Color.gold())
            # em_announce.add_field(name=f"Everyone has playing has died! **{first_name} WINS!!**",
            #                       value=f"With a final score of {first_score}")
            # em_announce.set_footer(text=f"The leaderboard is reset, and everyone came back to life")
            # await ctx.channel.send(embed=em_announce)
            # await ctx.channel.send(embed=em_board)
            # users = await get_player_data()
            # for player_id in users.keys():
            #     member_obj = await make_member(player_id)
            #     for roles in member_obj.roles:
            #         remove_role, role_name = await dead_person(roles.id, "remove role")
            #         if remove_role:
            #             dead_role = get(ctx.guild.roles, name=role_name)
            #             await member_obj.remove_roles(dead_role)
            #             await reset_data()
            #             client.get_command("visit").reset_cooldown(ctx)

            em_gift = discord.Embed(color=discord.Color.magenta())
            em_gift.add_field(name=f"{giver} is the only player alive!",
                              value="The game will reset at the end of the day")
            await ctx.channel.send(embed=em_gift)

    # no present to unbox is dark orange
    elif gift_type is False:
        em_gift = discord.Embed(color=discord.Color.red())
        em_gift.add_field(name="Inventory is empty!",
                          value="You need to `!visit` a player and receive a gift first to unbox it")
        em_gift.set_footer(text=f"{ctx.author} tried to unbox a gift")

        await ctx.channel.send(embed=em_gift)


@client.command()
async def decline(ctx):
    # same colors as before
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Guest")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # Checking if player is dead. Role specific.
    for role in ctx.author.roles:
        dead_unboxing = await dead_person(role.id, "dead declining")
        if dead_unboxing:
            em_dead = discord.Embed(color=discord.Color.red())
            em_dead.add_field(name="R.I.P", value=dead_unboxing, inline=True)
            em_dead.set_footer(text=f"{ctx.author} tried to decline a gift")
            await ctx.channel.send(embed=em_dead)
            return

    await playerData.add_player(ctx.author)
    user = ctx.author
    users = await playerData.get_player_data()
    gift_type = users[str(user.id)]["Received"]
    giver_id = users[str(user.id)]["Giver"]

    if gift_type == "nice" and giver_id is not False:
        giver = await client.fetch_user(giver_id)
        await playerData.update_stats(giver_id, 1, False, "Total Points")
        await playerData.update_stats(giver_id, 1, False, "Declined Points")
        await playerData.update_stats(ctx.author.id, 0, False, "Received")
        await playerData.update_stats(ctx.author.id, 0, False, "Giver")
        await playerData.update_stats(ctx.author.id, 0, True, "Join")
        await playerData.update_stats(giver_id, 0, True, "Join")

        # dark gray
        em_decline = discord.Embed(color=discord.Color.default())
        em_decline.add_field(name=f"**{ctx.author.name}** declined a **nice gift!**",
                             value=f"**{giver.name}** receives **1 point**")
        em_decline.set_footer(text=f"{ctx.author} declined a gift")
        await ctx.channel.send(embed=em_decline)

        await highscores.add_high_score(ctx.author)
        await highscores.add_high_score(giver)
        await highscores.update_high_score(giver_id, 1, False, "Old Score")
        scores = await highscores.get_high_score_data()
        if int(scores[str(giver_id)]["Old Score"]) > int(scores[str(giver_id)]["New Score"]):
            await highscores.update_high_score(giver.id, int(scores[str(giver_id)]["Old Score"]), True, "New Score")

    elif gift_type == "devious" and giver_id is not False:
        giver = await client.fetch_user(giver_id)
        await playerData.update_stats(ctx.author.id, 1, False, "Total Points")
        await playerData.update_stats(ctx.author.id, 1, False, "Accidental Kill")
        await playerData.update_stats(ctx.author.id, 0, False, "Received")
        await playerData.update_stats(ctx.author.id, 0, False, "Giver")
        await playerData.update_stats(giver_id, 0, True, "Dead")
        await playerData.update_stats(ctx.author.id, 0, True, "Join")
        await playerData.update_stats(giver_id, 0, True, "Join")

        em_bomb = discord.Embed(color=discord.Color.fuchsia())
        em_bomb.add_field(
            name=f"**{ctx.author.name}** declined an explosive **devious gift** and receives **1 point**!",
            value=f"**{giver.name}** receives a bomb and **dies**")
        em_bomb.set_footer(text=f"{ctx.author} declined a gift")
        await ctx.channel.send(embed=em_bomb)

        giver_obj = await make_member(giver_id)
        dead_role = get(ctx.guild.roles, name="Dead")
        await giver_obj.add_roles(dead_role)

        await highscores.add_high_score(ctx.author)
        await highscores.add_high_score(giver)
        await highscores.update_high_score(ctx.author.id, 1, False, "Old Score")
        await highscores.update_high_score(giver_id, 1, False, "Deaths")
        scores = await highscores.get_high_score_data()
        if int(scores[str(ctx.author.id)]["Old Score"]) > int(scores[str(ctx.author.id)]["New Score"]):
            await highscores.update_high_score(ctx.author.id, int(scores[str(ctx.author.id)]["Old Score"]), True, "New Score")

        win = await playerData.check_winner()
        if win:
            # final leaderboard is dark gold
            # title, name_list, value_list, status = await make_leaderboard(True)
            # em_board = discord.Embed(title=title, color=discord.Color.orange())
            # for num in range(len(name_list)):
            #     em_board.add_field(name=name_list[num],
            #                        value=value_list[num] + " \n" + status[num])
            # first_name = name_list[0]
            # first_score = value_list[0]
            # # winner announcement is gold
            # em_announce = discord.Embed(color=discord.Color.gold())
            # em_announce.add_field(name=f"Everyone has playing has died! **{first_name} WINS!!**",
            #                       value=f"With a final score of {first_score}")
            # em_announce.set_footer(text=f"The leaderboard is reset, and everyone came back to life")
            # await ctx.channel.send(embed=em_announce)
            # await ctx.channel.send(embed=em_board)
            # users = await get_player_data()
            # for player_id in users.keys():
            #     member_obj = await make_member(player_id)
            #     for roles in member_obj.roles:
            #         remove_role, role_name = await dead_person(roles.id, "remove role")
            #         if remove_role:
            #             dead_role = get(ctx.guild.roles, name=role_name)
            #             await member_obj.remove_roles(dead_role)
            #             await reset_data()
            #             client.get_command("visit").reset_cooldown(ctx)

            em_gift = discord.Embed(color=discord.Color.magenta())
            em_gift.add_field(name=f"{ctx.author} is the only player alive!",
                              value="The game will reset at the end of the day")
            await ctx.channel.send(embed=em_gift)

    # no present to unbox is dark orange
    elif gift_type is False:
        em_gift = discord.Embed(color=discord.Color.red())
        em_gift.add_field(name="Inventory is empty!",
                          value="You need to `!visit` a player and receive a gift first to decline it")
        em_gift.set_footer(text=f"{ctx.author} tried to decline a gift")
        await ctx.channel.send(embed=em_gift)


@client.command()
async def trash(ctx):
    # Wrong chat is brand red
    msg = await wrong_chat(ctx.channel.id, ctx.guild, "Guest")
    if msg:
        em_wrong_c = discord.Embed(color=discord.Color.brand_red())
        em_wrong_c.add_field(name="Wrong Chat", value=msg, inline=True)
        await ctx.author.send(embed=em_wrong_c)
        return

    # Checking if player is dead. Role specific.
    for role in ctx.author.roles:
        dead_unboxing = await dead_person(role.id, "dead trashing")
        if dead_unboxing:
            em_dead = discord.Embed(color=discord.Color.red())
            em_dead.add_field(name="R.I.P", value=dead_unboxing, inline=True)
            em_dead.set_footer(text=f"{ctx.author} tried to trash a gift")
            await ctx.channel.send(embed=em_dead)
            return

    await playerData.add_player(ctx.author)
    user = ctx.author
    users = await playerData.get_player_data()
    gift_type = users[str(user.id)]["Received"]
    giver_id = users[str(user.id)]["Giver"]
    trash_cap = users[str(user.id)]["Trashability"]

    if gift_type is False:
        em_empty = discord.Embed(color=discord.Color.red())
        em_empty.add_field(name="Inventory is empty!",
                           value="You need to `!visit` a player and receive a gift first to trash it")
        em_empty.set_footer(text=f"{ctx.author} tried to trash a gift")
        await ctx.channel.send(embed=em_empty)

    # throwing gift away is teal
    elif trash_cap and giver_id is not False:
        giver = await client.fetch_user(giver_id)
        await playerData.update_stats(ctx.author.id, -1, False, "Trashability")
        await playerData.update_stats(ctx.author.id, 0, False, "Received")
        await playerData.update_stats(ctx.author.id, 0, False, "Giver")

        em_trash = discord.Embed(color=discord.Color.green())
        em_trash.add_field(name=f"You threw away {giver.name}'s {gift_type} gift!",
                           value=f"**Trashability** decreased by 1")
        em_trash.set_footer(text=f"{ctx.author} trashed a gift")
        await ctx.channel.send(embed=em_trash)

    # not enough trash cap is dark teal
    elif not trash_cap and giver_id is not False:
        giver = await client.fetch_user(giver_id)
        em_none = discord.Embed(color=discord.Color.red())
        em_none.add_field(name=f"Not enough **trashability** to throw away {giver.name}'s gift!",
                          value="You need at least **1 trashability** which can be gained from unboxing **nice gifts**")
        em_none.set_footer(text=f"{ctx.author} tried to trash a gift")

        await ctx.channel.send(embed=em_none)


client.run(tokens.key)
