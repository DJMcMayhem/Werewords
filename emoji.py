class Emoji():

    emoji_list = {
            ":joy:" : "\U0001F602",
            ":x:" : "\U0000274C",
            ":white_check_mark:" : "\U00002705",
            ":wave:" : "\U0001F44B",
            ":thumbs_up:" : "\U0001F44D",
            ":question:" : "\U00002753",

        }

    def __init__(self, emoji):
        self.emoji = Emoji.emoji_list[emoji.lower()]

    def __repr__(self):
        return "Emoji({})".format(self.emoji)

    def __str__(self):
        return self.emoji
