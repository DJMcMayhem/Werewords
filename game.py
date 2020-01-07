import random

class Player():
    def __init__(self, user, role):
        self.user = user
        self.role = role
        self.questions = { "yes" : 0, "no" : 0, "maybe": 0 }

class Game():
    def __init__(self, players, mayor):
        self.players = players

        self.mayor = mayor

        self.roles = ["Werewolf", "Seer"]
        self.roles += (["Villager"] * (len(players) - 2))

        random.shuffle(self.roles)

        self.role_msg = ""

        for player, role in zip(self.players, self.roles):
            self.role_msg += "{}: {}\n".format(player.name, role)

        with open("wordlist.txt") as words:
            self.words = [word.strip() for word in words.readlines()]

        self.game_state = "Waiting for Mayor to pick a word."
        self.pending_questions = []
        self.answered_questions = []
        self.tokens_left = 36
        self.end_time = 0

    def get_user_role(self, user):
        try:
            i = self.players.index(user)
            return self.roles[i]
        except:
            return "Unkown"

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


