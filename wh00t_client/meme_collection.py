# Meme Collection base class

import time
from bin.emojis import Emojis
from bin.help import HelpMeme


class MemeCollection:
    def meme(self, client_socket, meme_type):
        ascii_array = ['meme type "{}" not recognized'.format(meme_type)]

        if meme_type == 'wise':
            ascii_array = self.wise_ascii()
        elif meme_type == 'tableFlip':
            ascii_array = self.table_flip_ascii()
        elif meme_type == 'hurry':
            ascii_array = self.hurry_ascii()
        elif meme_type == 'bye':
            ascii_array = self.bye_ascii()
        elif meme_type == 'hug':
            ascii_array = self.hug_ascii()
        elif meme_type == 'shrug':
            ascii_array = self.shrug_ascii()
        elif meme_type == 'kitty':
            ascii_array = self.kitty_ascii()
        elif meme_type == 'luv':
            ascii_array = self.luv_ascii()

        for artLine in ascii_array:
            client_socket.send(bytes(artLine, 'utf8'))
            time.sleep(.025)

    @staticmethod
    def print_emojis_help():
        emoji_help = '\n'
        for item in Emojis:
            emoji_help += '\n     {}  {}'.format(Emojis[item], item)
        return emoji_help

    @staticmethod
    def print_memes_help():
        client_memes = '\n'
        for item in HelpMeme:
            client_memes += '\n     {}'.format(item)
        return client_memes

    @staticmethod
    def wise_ascii():
        return ["         {o,o}",
                "         |)__)",
                "          -\"-\"-"]

    @staticmethod
    def table_flip_ascii():
        return ["        (ノ ゜Д゜)ノ ︵ ┻━┻"]

    @staticmethod
    def hurry_ascii():
        return ["       ─=≡Σ((( つ◕ل͜◕)つ"]

    @staticmethod
    def bye_ascii():
        return ["       (ʘ‿ʘ)╯"]

    @staticmethod
    def hug_ascii():
        return ["       (づ｡◕‿‿◕｡)づ"]

    @staticmethod
    def shrug_ascii():
        return ["       ¯\_(ツ)_/¯"]

    @staticmethod
    def kitty_ascii():
        return ["       =^_^="]

    @staticmethod
    def luv_ascii():
        return ["                  ▄▀▀▀▄▄▄▄▄▄▄▀▀▀▄",
                "                  █▒▒░░░░░░░░░▒▒█",
                "                     █░░█░░░░░█░░█     LUVS YOU",
                "               ▄▄   █░░░▀█▀░░░█    ▄▄",
                "            █░░█ ▀▄░░░░░░░▄▀ █░░█"]
