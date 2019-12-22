import random

class Player():
    def __init__(self, user, role):
        self.user = user
        self.role = role
        self.questions = { "yes" : 0, "no" : 0, "maybe": 0 }

class Game():
    def __init__(self, players):
        self.players = players

        self.mayor = random.choice(players)

        self.roles = ["Werewolf", "Seer"]
        self.roles += (["Villager"] * (len(players) - 2))

        random.shuffle(self.roles)

        for player, role in zip(self.players, self.roles):
            print("{}: {}".format(player, role))

        print("{} Chosen as Mayor!".format(self.mayor))

        with open("wordlist.txt") as words:
            self.words = [word.strip() for word in words.readlines()]

        self.game_state = "Waiting for Mayor to pick a word."

    def get_user_role(self, user):
        try:
            i = self.players.index(user)
            return self.roles[i]
        except:
            return "Unkown"

    def state(self):
        return self.game_state

    def get_word_choices(self):
        random.shuffle(self.words)

        return self.words[:3]

    def choose_word(self, word):
        self.game_state = "Game in progress."
        self.word = word

    def get_werewolves(self):
        wolves = []

        for player, role in zip(self.players, self.roles):
            if role == "Werewolf":
                wolves.append(player)

        return wolves
