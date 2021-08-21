# Meme Collection base class

from typing import List
from bin.emojis import Emojis
from bin.help import HelpMeme


class MemeCollection:
    def meme(self, meme_type) -> List[str]:
        ascii_array: List[str] = [f':face_with_raised_eyebrow: Sorry, '
                                  f'meme type "{meme_type}" doesn\'t exist.']
        if meme_type == 'tableFlip':
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
        return ascii_array

    @staticmethod
    def print_emojis_help() -> str:
        emoji_help: str = '\n'
        for item in Emojis:
            emoji_help += f'\n     {Emojis[item]}  {item}'
        return f'{emoji_help}\n'

    @staticmethod
    def print_memes_help() -> str:
        client_memes: str = '\n'
        for item in HelpMeme:
            client_memes += f'\n     {item}'
        return f'{client_memes}\n'

    @staticmethod
    def table_flip_ascii() -> List[str]:
        return ["        (ノ ゜Д゜)ノ ︵ ┻━┻"]

    @staticmethod
    def hurry_ascii() -> List[str]:
        return ["       ─=≡Σ((( つ◕ل͜◕)つ"]

    @staticmethod
    def bye_ascii() -> List[str]:
        return ["       (ʘ‿ʘ)╯"]

    @staticmethod
    def hug_ascii() -> List[str]:
        return ["       (づ｡◕‿‿◕｡)づ"]

    @staticmethod
    def shrug_ascii() -> List[str]:
        return ["       ¯\_(ツ)_/¯"]

    @staticmethod
    def kitty_ascii() -> List[str]:
        return ["       =^_^="]

    @staticmethod
    def luv_ascii() -> List[str]:
        return ["                  ▄▀▀▀▄▄▄▄▄▄▄▀▀▀▄",
                "                  █▒▒░░░░░░░░░▒▒█",
                "                     █░░█░░░░░█░░█     LUVS YOU",
                "               ▄▄   █░░░▀█▀░░░█    ▄▄",
                "            █░░█ ▀▄░░░░░░░▄▀ █░░█"]
