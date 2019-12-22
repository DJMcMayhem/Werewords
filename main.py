import discord
from emoji import Emoji
import time
import sys
import bot

client = discord.Client()

dude = bot.Bot(client)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await dude.handle_message(message)
    return


    if message.content.startswith("!hello"):
        await message.channel.send('hello!')

    if message.content.startswith("!members"):
        members = message.channel.members

        member_string = ", ".join(member.name for member in members)

        await message.channel.send("i can see {} members: {}".format(len(members), member_string))

    if message.content.startswith("!react"):
        await message.add_reaction(str(emoji(":joy:")))

    if message.content.startswith("!yesorno"):
        poll_message = await message.channel.send("yes or no")

        await poll_message.add_reaction(str(emoji(":white_check_mark:")))

        await poll_message.add_reaction(str(emoji(":x:")))

        time.sleep(10)

        no = -1
        yes = -1

        # update poll_message
        poll_message = await message.channel.fetch_message(poll_message.id)

        for reaction in poll_message.reactions:
            if str(reaction) == str(emoji(":white_check_mark:")):
                yes += reaction.count
            elif str(reaction) == str(emoji(":x:")):
                no += reaction.count

        await message.channel.send("votes yes: {}, no: {}".format(yes, no))

    if message.content.startswith("!purge"):
        await message.channel.purge()

    if message.content.startswith("!kill"):
        await message.channel.send("goodbye cruel world!")

        time.sleep(3)

        sys.exit()

    if message.content.startswith("!dm"):
        user = message.author

        dm = user.dm_channel

        if dm is none:
            dm = await user.create_dm()

        await dm.send("hello {}!".format(user.name))

    if message.content.startswith("!type"):
        async with message.channel.typing():
            time.sleep(10)

            await message.channel.send("asdklfjasdlkfjasdl;")

with open("token.txt") as f:
    token = f.read().strip()

client.run(token)
