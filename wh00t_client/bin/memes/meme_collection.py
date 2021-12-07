# Meme Collection base class
from typing import List
from .memes import Memes


class MemeCollection:
    def __init__(self):
        self._supported_ascii_memes: dict = Memes
        self._supported_ascii_memes = dict(sorted(self._supported_ascii_memes.items()))

    def meme(self, meme_type: str) -> List[str]:
        ascii_array: List[str] = [f':face_with_raised_eyebrow: Sorry, '
                                  f'meme type "{meme_type}" does not exist.']
        if meme_type in self._supported_ascii_memes.keys():
            ascii_array = self._supported_ascii_memes[meme_type]['meme']
        return ascii_array

    def print_memes_help(self) -> str:
        client_memes: str = '\n'
        for meme_text in self._supported_ascii_memes.keys():
            client_memes += f'\n     /meme - {self._supported_ascii_memes[meme_text]["help_text"]}'
        return f'{client_memes}\n'
