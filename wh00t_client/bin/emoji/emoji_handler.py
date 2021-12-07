# Chat Client Emojis Supported by Paging
import tkinter
from typing import List
from bin.emoji.emojis import Emojis


class EmojiHandler:
    def __init__(self, chat_message: tkinter.StringVar, message_input_field: tkinter.Entry):
        self._chat_message: tkinter.StringVar = chat_message
        self._message_input_field: tkinter.Entry = message_input_field
        self._emoji_dict_keys: List[str] = list(Emojis.keys())
        self._emoji_paging_index: int = 0
        self._emoji_sentence_lock: bool = False

    @staticmethod
    def print_emojis_help() -> str:
        emoji_help: str = '\n'
        for item in Emojis:
            emoji_help += f'\n     {Emojis[item]}  {item}'
        return f'{emoji_help}\n'

    def get_emoji_sentence_lock(self):
        return self._emoji_sentence_lock

    def get_emoji_dict_keys(self):
        return self._emoji_dict_keys

    def get_emoji_paging_index(self):
        return self._emoji_paging_index

    def set_emoji_paging_index(self, current_index: int):
        self._emoji_paging_index = current_index

    def set_emoji_sentence_lock(self, is_locked: bool):
        self._emoji_sentence_lock = is_locked

    def emoji_message_cache(self, message_cache: str) -> str:
        message_cache: str = message_cache
        if not self._emoji_sentence_lock and (self._chat_message.get() not in self._emoji_dict_keys):
            self.set_emoji_sentence_lock(True)
            message_cache = self._chat_message.get()
        return message_cache

    def emoji_message_cache_check_not_empty(self, message_cache: str) -> None:
        if not message_cache.replace(' ', ''):
            self.set_emoji_sentence_lock(False)

    def emoji_message_handler(self, message: str, message_cache: str) -> None:
        self.set_emoji_sentence_lock(False)
        self._chat_message.set(f'{message_cache}{message}')
        self._message_input_field.icursor(len(self._chat_message.get()))
