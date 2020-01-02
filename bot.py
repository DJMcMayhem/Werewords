from emoji import Emoji
import time
import sys
import game
import discord
import re
import threading

class Bot():
    def __init__(self, client):
        self.prefix = "!"
        self.commands = {
            "hello" : [Bot.hello, "Greet the user."],
            "members" : [Bot.members, "Print all the member the bot can see."],
            "react" : [Bot.react, "React to your message with :joy:"],
            "yesorno" : [Bot.yes_or_no, "Do a yes or no poll."],
            "purge" : [Bot.purge, "Delete all messages in the current room."],
            "kill" : [Bot.kill, "Turn the bot off."],
            "dm" : [Bot.dm, "Send the user a direct message."],
            "type" : [Bot.type, "Type for a little while."],
            "newgame" : [Bot.newgame, "Start a new game of wereword."],
            "state" : [Bot.state, "Print the state of the current game."],
            "roles" : [Bot.roles, "Print each member in the game and what role they were."],
            "endgame" : [Bot.game_over, "End the current game"],
            "help" : [Bot.help, "Show the available commands."]
        }

        self.client = client
        self.current_game = None

    async def bot_loop(self):
        if self.current_game is None:
            return

        if self.current_game.game_state == "Game in progress.":
            if time.time() > self.current_game.end_time > 0:
                await self.end_game(False, "You have ran out of time!")

            if self.current_game.tokens_left == 0:
                await self.end_game(False, "You have used up your tokens!")

    async def send_dm(self, user, message):
        dm = user.dm_channel

        if dm is None:
            dm = await user.create_dm()

        await dm.send(message)

    async def handle_message(self, message):
        if message.content.startswith(self.prefix):
            com = message.content[1:]
            for com, data in self.commands.items():
                if message.content[1:].startswith(com):
                    func = data[0]
                    await func(self, message)
                    return

        if self.current_game is not None:
            if type(message.channel) is discord.channel.DMChannel:
                await self.handle_dm(message)

            elif match := re.match("^\*\*.*\*\*", message.content):
                await self.handle_game_message(message)

    async def handle_dm(self, message):
        if message.author == self.current_game.mayor:
            if self.current_game.game_state == "Waiting for Mayor to pick a word.":
                if message.content in "123":
                    i = int(message.content)
                    word = self.word_choices[i-1]

                    self.current_game.choose_word(word)

                    await message.channel.send(":thumbsup:")

                    for i, player in enumerate(self.current_game.players):
                        if self.current_game.roles[i] in ["Werewolf", "Seer"] and player != self.current_game.mayor:
                            await self.send_dm(player, "The mayor chose the word: {}".format(word))

                    await self.game_channel.send("The game has started!")

                    self.current_game.end_time = time.time() + (5 * 60)

    async def end_game(self, word_guessed, message):
        await self.game_channel.send(message)

        if not word_guessed:
            self.current_game.game_state = "Voting for Werewolf."

            await self.game_channel.send("The secret word was: {}".format(self.current_game.word))

            await self.game_channel.send("Now you must vote on who you think the werewolf was")

        else:
            self.current_game.game_state = "Voting for Seer."

            wolves = self.current_game.get_werewolves()

            msg = "The werewolf was {}"

            if len(wolves) > 1:
                msg = "The werewolves were {}"

            await self.game_channel.send(msg.format(", ".join(wolf.name for wolf in wolves)))
            await self.game_channel.send("They will vote on who they think the seer was.")

    async def handle_game_message(self, message):
        if self.current_game.game_state == "Game in progress.":
            print("That was a game message!")

            if message.author == self.current_game.mayor:
                return
 
            if match := re.search("^\*\*(.*)\*\*$", message.content):
                self.current_game.pending_questions.append(message)

                await message.add_reaction(str(Emoji(":white_check_mark:")))
                await message.add_reaction(str(Emoji(":x:")))
                await message.add_reaction(str(Emoji(":question:")))

                correct = discord.utils.get(message.channel.guild.emojis, name="correct")
                await message.add_reaction(correct)

    async def handle_reaction_add(self, reaction, user):
        if reaction.message in self.current_game.pending_questions and user == self.current_game.mayor:

            if type(reaction.emoji) is discord.Emoji:
                if reaction.emoji.name == "correct":
                    await self.end_game(True, "You have guessed the word!")

            if str(reaction) in (str(Emoji(":white_check_mark:")), str(Emoji(":x:"))):
                self.current_game.tokens_left -= 1

            self.current_game.pending_questions.remove(reaction.message)

            print(self.current_game.tokens_left)

    async def hello(self, message):
        await message.channel.send('hello!')

    async def members(self, message):
        members = message.channel.members

        member_string = ", ".join(member.name for member in members)

        await message.channel.send("I can see {} members: {}".format(len(members), member_string))

    async def react(self, message):
        await message.add_reaction(str(Emoji(":joy:")))

    async def yes_or_no(self, message):
        poll_message = await message.channel.send("Yes or No")

        await poll_message.add_reaction(str(Emoji(":white_check_mark:")))

        await poll_message.add_reaction(str(Emoji(":x:")))

        time.sleep(10)

        no = -1
        yes = -1

        # update poll_message
        poll_message = await message.channel.fetch_message(poll_message.id)

        for reaction in poll_message.reactions:
            if str(reaction) == str(Emoji(":white_check_mark:")):
                yes += reaction.count
            elif str(reaction) == str(Emoji(":x:")):
                no += reaction.count

        await message.channel.send("Votes yes: {}, no: {}".format(yes, no))

    async def purge(self, message):
        if any(role.name == "bot admin" for role in message.author.roles):
            await message.channel.purge()
        else:
            await message.channel.send("You do not have permission to purge messages")

    async def kill(self, message):
        if not any(role.name == "bot admin" for role in message.author.roles):
            await message.channel.send("You do not have permission to kill me")
            return

        goodbye = await message.channel.send("Goodbye cruel world!")

        await goodbye.add_reaction(str(Emoji(":wave:")))

        time.sleep(3)

        sys.exit()

    async def dm(self, message):
        await self.send_dm(message.author, "Hello {}!".format(message.author.name))

    async def type(self, message):
        async with message.channel.typing():
            time.sleep(10)

            await message.channel.send("asdklfjasdlkfjasdl;")

    async def newgame(self, message):
        self.game_channel = message.channel

        players = message.mentions

        if self.client.user in players:
            players.remove(self.client.user)

        if len(players) < 2:
            await message.channel.send("You must @mention at least two players to start a game.")
            return

        await message.channel.send("Players: {}".format(", ".join(member.name for member in message.mentions)))

        self.current_game = game.Game(players)

        await message.channel.send("Mayor: {}".format(self.current_game.mayor.name))
        await message.channel.send("Roles: {}".format(", ".join(sorted(self.current_game.roles))))

        for user in players:
            msg = ""

            if user == self.current_game.mayor:
                msg += "You are the Mayor!\n"
                # await self.send_dm(user, "You are the Mayor!")

            role = self.current_game.get_user_role(user)

            msg += "Your secret role is: {}\n".format(role)
            # await self.send_dm(user, "Your secret role is: {}".format(role))

            if role == "Werewolf":
                other_wolves = self.current_game.get_werewolves()
                other_wolves.remove(user)

                if len(other_wolves) > 0:
                    msg += "The other werewolves are: {}\n".format(", ".join(wolf.name for wolf in other_wolves))

            if user == self.current_game.mayor:
                self.word_choices = self.current_game.get_word_choices()
                word_choices_str = "\n".join("{}: {}".format(i + 1, word) for i, word in enumerate(self.word_choices))

                msg += "Please choose a word:\n{}".format(word_choices_str)

            await self.send_dm(user, msg)

    async def roles(self, message):
        if None in (self.game_channel, self.current_game):
            return

        await self.game_channel.send(self.current_game.role_msg)

    async def game_over(self, message):
        await self.roles(message)

        self.current_game = None

    async def state(self, message):
        if self.current_game is None:
            await message.channel.send("No game running.")
            return

        await message.channel.send(self.current_game.game_state)
        if self.current_game.game_state == "Game in progress." and self.current_game.end_time > 0:
            await message.channel.send("{} seconds left".format(int(self.current_game.end_time - time.time())))

    async def help(self, message):
        await message.channel.send("\n".join("{} -> {}".format(com, com_data[1]) for com, com_data in self.commands.items()))
