import discord


# wrong chat messages
async def send_basic_wc(channel, author):
    em_wrong_c = discord.Embed(color=discord.Color.brand_red())
    em_wrong_c.add_field(name="Wrong Chat",
                         value=f"You can't use this command in this channel, "
                               f"only in **#{channel}** or in **DM with the bot**", inline=True)
    await author.send(embed=em_wrong_c)


async def send_guest_wc(channel, author):
    em_wrong_c = discord.Embed(color=discord.Color.brand_red())
    em_wrong_c.add_field(name="Wrong Chat", value=f"You can't use this command in this channel or in the DM with the "
                                                  f"bot, only in **#{channel}**", inline=True)
    await author.send(embed=em_wrong_c)


# dead players messages
async def send_author_d(channel, author, player):
    em_dead_a = discord.Embed(color=discord.Color.red())
    em_dead_a.add_field(name="R.I.P", value="You have **died** and can't use this command", inline=True)
    em_dead_a.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_dead_a)


async def send_player_d(channel, author, player):
    em_dead_a = discord.Embed(color=discord.Color.red())
    em_dead_a.add_field(name="R.I.P", value="The host you tried to visit have **died**, "
                                            "you would be visiting a haunted house", inline=True)
    em_dead_a.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_dead_a)


# basic command messages
async def send_rules(channel):
    # Rules and commands are og_blurple
    em_rules = discord.Embed(title="Here are the Basic Rules:", color=discord.Color.og_blurple())
    em_rules.add_field(name="The Main Goal is to Earn as Many Points as Possible Without Dying!",
                       value="\n"  # how many minutes
                             "\n**1.** Every idk minutes, you may **visit** other players and act as the guest\n"
                             "\n**2.** The player you visited will act as the host\n"
                             "\n**3.** The host will have the option to give the guest a **nice** gift or a "
                             "**devious** gift\n "
                             "> *The guest can go back **home** if the host hasn't given them a gift yet*\n"
                             "\n**4.** After receiving a gift, the guest can **unbox**, **decline** or **trash** "
                             "the"
                             "gift "
                             "\n> Unboxing a **nice gift**: The guest will gain **1 point** and **1 trashability**"
                             "\n> Unboxing a **devious gift**: The guest will **DIE** and the host will gain **1 "
                             "point**\n> "
                             "\n> Declining a **nice gift**: The host will gain **1 point**"
                             "\n> Declining a **devious gift**: The host will **DIE** and the guest will gain **1 "
                             "point**\n> "
                             "\n> Thrashing **ANY gift**: The gift is forever **GONE**; the gift type will be "
                             "revealed"
                             "\n>> *Trashing a gift will use up **1 trashability***\n "
                             "\n**5.** If a player visits you, they will act as the guest and you will act as the "
                             "host\n")
    em_rules.set_footer(text="You can only visit and get visited by one player at a time\n"
                             "You can't visit anyone while a gift has not been unboxed, declined or trashed\n"
                             ">> For the list of commands, type `!guide`")

    await channel.send(embed=em_rules)


async def send_guide(channel):
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

    await channel.send(embed=em_commands)


async def send_stats(user, total, trashability, nice_amt, accident_amt, decline_amt, kills_amt,
                     author, send_here):
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

    em_stat.set_footer(text=f"Requested by: {author}")
    await send_here(embed=em_stat)


async def send_leaderboards(title, name_list, value_list, status, channel):
    em_board = discord.Embed(title=title, color=discord.Color.orange())

    for num in range(len(name_list)):
        em_board.add_field(name=name_list[num],
                           value=value_list[num] + " \n" + status[num])

    await channel.send(embed=em_board)


async def send_highscores(name_list, value_list, death_list, channel):
    em_board = discord.Embed(title="The Current High Scores: ", color=discord.Color.orange())

    for num in range(len(name_list)):
        em_board.add_field(name=name_list[num],
                           value=value_list[num] + " \n" + death_list[num])

    await channel.send(embed=em_board)


# visiting commands messages
async def send_v_someone_else(currently_visiting, player, author, channel):
    em_else = discord.Embed(color=discord.Color.red())
    em_else.add_field(name=f"You are already at {currently_visiting.name}'s house!",
                      value=f"If you want to visit {player.name} instead, you need to go home first")
    em_else.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_else)


async def send_v_already(player, author, channel):
    em_here = discord.Embed(color=discord.Color.red())
    em_here.add_field(name=f"You have arrived at {player.name}'s house a long time ago!",
                      value=f"Wait for {player.name} to pick a gift for you, or if you don't want to"
                            f" wait, "
                            f"go home")
    em_here.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_here)


async def send_guest_at_host(player, guest, author, channel):
    em_full = discord.Embed(color=discord.Color.red())
    em_full.add_field(name=f"{player.name}'s house is full, as {guest.name} is already there!",
                      value=f"Visit {player.name} at a later time or visit somebody else")
    em_full.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_full)


async def send_guest_at_home(player, guest, author, channel):
    em_leave = discord.Embed(color=discord.Color.red())
    em_leave.add_field(name=f"{guest.name} is at your house!",
                       value=f"Give {guest.name} a gift first before you "
                             f"are able to visit {player}")
    em_leave.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_leave)


async def send_not_home(player, host, author, channel):
    em_empty = discord.Embed(color=discord.Color.red())
    em_empty.add_field(name=f"{player.name} is at {host.name}'s house!",
                       value=f"Wait for {player.name} to return home before visiting {player.name}")
    em_empty.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_empty)


async def send_full_inventory(player, author, channel):
    em_gift = discord.Embed(color=discord.Color.red())
    em_gift.add_field(name="Your inventory is full!",
                      value=f"Unbox, decline or trash the previous gift before visiting {player.name}")
    em_gift.set_footer(text=f"{author} tried to visit {player}")
    await channel.send(embed=em_gift)


async def send_visiting_player(player, author, channel):
    em_host = discord.Embed(color=discord.Color.blue())
    em_host.add_field(name=f"{author.name} has come to visit!",
                      value=f"Choose a `!nice` or a `!devious` gift for {author.name}")
    em_host.set_footer(text=f"{author} arrived at {player}'s home")
    await player.send(embed=em_host)

    em_guest = discord.Embed(color=discord.Color.green())
    em_guest.add_field(name=f"You have arrived!",
                       value=f"Now wait as {player.name} will pick the perfect gift for you...")
    em_guest.set_footer(text=f"{author} is waiting for a gift at {player}'s home")
    await channel.send(embed=em_guest)


async def send_home_already(author, channel):
    em_home = discord.Embed(color=discord.Color.red())
    em_home.add_field(name="You are already home!",
                      value="Visit someone first and then you can decide to go home")
    em_home.set_footer(text=f"{author} tried to go home")
    await channel.send(embed=em_home)


async def send_received_already(author, channel):
    em_gift = discord.Embed(color=discord.Color.red())
    em_gift.add_field(name="The host has given you a gift already!",
                      value="You cannot leave their house until you unbox, decline or trash the gift")
    em_gift.set_footer(text=f"{author} tried to go home")
    await channel.send(embed=em_gift)


async def send_go_home(player, author, channel):
    em_host = discord.Embed(color=discord.Color.blue())
    em_host.add_field(name=f"{author.name} has went home :(",
                      value=f"You took too long to give them a gift, "
                            f"{author.name} got tired of waiting")
    em_host.set_footer(text=f"{author} went home")
    await player.send(embed=em_host)

    em_guest = discord.Embed(color=discord.Color.green())
    em_guest.add_field(name=f"You have arrived home from {player.name}'s house",
                       value=f"You can visit a host")
    em_guest.set_footer(text=f"{author} went home")
    await channel.send(embed=em_guest)


# Easter Egg messages
async def send_bot_stats(author, send_here):
    em_bot_stat = discord.Embed(title="Present Delivery Bot's Stats", color=discord.Color.purple())
    em_bot_stat.add_field(name="Total Points", value=999)
    em_bot_stat.set_footer(text=f"{author} has found an easter egg")
    await send_here(embed=em_bot_stat)


async def send_bot_visit(author):
    em_bot_visit = discord.Embed(color=discord.Color.purple())
    em_bot_visit.add_field(
        name="Thanks for coming, I have nothing for you though. Try visiting **players**",
        value="I will teleport you back to where you were")
    em_bot_visit.set_footer(text=f"{author} has found an easter egg")
    await author.send(embed=em_bot_visit)


async def send_visit_self(author, channel):
    em_self = discord.Embed(color=discord.Color.red())
    em_self.add_field(name="You can't visit yourself!",
                      value="How is that possible??")
    em_self.set_footer(text=f"{author} has found an easter egg")
    await channel.send(embed=em_self)


async def send_visit_no_one(author, channel):
    em_none = discord.Embed(color=discord.Color.red())
    em_none.add_field(name="You have not specified who you are visiting!",
                      value="To visit a host, type the command and mention the player you want to visit")
    em_none.set_footer(text=f"{author} has found an easter egg")
    await channel.send(embed=em_none)
