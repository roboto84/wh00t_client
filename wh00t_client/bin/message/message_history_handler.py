
import logging
import tkinter
from client_settings import ClientSettings
from typing import Optional, List
from bin.emoji.emoji_handler import EmojiHandler


class MessageHistoryHandler:
    def __init__(self, logging_object: logging, client_settings: ClientSettings, emoji_handler: EmojiHandler,
                 chat_message: tkinter.StringVar,
                 message_input_field: tkinter.Entry, message_list: tkinter.Text):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging_object.INFO)
        self._chat_message: tkinter.StringVar = chat_message
        self._message_input_field: tkinter.Entry = message_input_field
        self._client_settings: ClientSettings = client_settings
        self._message_list: tkinter.Text = message_list
        self._emoji_handler: EmojiHandler = emoji_handler
        self._message_list_message_history: List[str] = []
        self._message_cache: Optional[str] = None
        self._message_hyperlinks: List[dict] = []
        self._message_history_index: int = 0

    def get_emoji_sentence_lock(self):
        return self._emoji_handler.get_emoji_sentence_lock()

    def emoji_message_handler(self, message: str):
        return self._emoji_handler.emoji_message_handler(message, self._message_cache)

    def message_list_event_handler(self, event) -> Optional[str]:
        self._logger.debug(str(event))
        if event.keycode == 67 and event.keysym == 'c':  # Windows
            return
        elif event.char and event.char == '\x03' and event.keycode == 54 and event.keysym == 'c':  # Linux
            return
        else:
            return 'break'

    def message_history_handler(self, message: str) -> None:
        self._message_list_message_history.append(message)
        if len(self._message_list_message_history) > 10:
            del self._message_list_message_history[0]
        self._message_history_index = len(self._message_list_message_history) - 1
        self._chat_message.set('')

    def _page_up_page_down(self, comparator: bool, emoji_paging_index: int, new_emoji_paging_index: int):
        new_index: int = emoji_paging_index
        if comparator:
            new_index: int = new_emoji_paging_index
        self._emoji_handler.set_emoji_paging_index(new_index)
        self._logger.debug(f'index: {new_index}')
        self._chat_message.set(self._emoji_handler.get_emoji_dict_keys()[new_index])
        self._message_input_field.icursor(len(self._chat_message.get()))

    def message_entry_event_handler(self, event) -> None:
        self._logger.debug(str(event))
        emoji_paging_index = self._emoji_handler.get_emoji_paging_index()
        if event.keysym == 'Escape':
            if self._emoji_handler.get_emoji_sentence_lock():
                self._chat_message.set(self._message_cache)
                self._emoji_handler.set_emoji_sentence_lock(False)
            else:
                self._chat_message.set(self._client_settings.get_exit_command())
            self._message_input_field.icursor(len(self._chat_message.get()))
        elif event.keysym == 'Up':
            if self._message_history_index < 0:
                self._message_history_index = len(self._message_list_message_history) - 1
            if len(self._message_list_message_history) != 0:
                self._chat_message.set(self._message_list_message_history[self._message_history_index])
                self._message_input_field.icursor(len(self._chat_message.get()))
                self._message_history_index -= 1
        elif event.keysym == 'Down':
            self._emoji_handler.set_emoji_paging_index(0)
            self._message_history_index = len(self._message_list_message_history) - 1
            self._chat_message.set('')
            self._message_cache = ''
        elif (event.keysym == 'Prior') or (event.keysym == 'Next'):
            first_emoji = self._chat_message.get() not in self._emoji_handler.get_emoji_dict_keys()
            self._message_cache = self._emoji_handler.emoji_message_cache(self._message_cache)
            if event.keysym == 'Prior':
                emoji_paging_index += 1
                index_limit: int = len(self._emoji_handler.get_emoji_dict_keys()) - 1
                self._logger.debug(f'index_limit: {index_limit}')
                new_possible_index: int = 0
                self._page_up_page_down((first_emoji or (emoji_paging_index > index_limit)),
                                        emoji_paging_index, new_possible_index)
            elif event.keysym == 'Next':
                emoji_paging_index -= 1
                new_possible_index: int = len(self._emoji_handler.get_emoji_dict_keys()) - 1
                self._page_up_page_down((first_emoji or (emoji_paging_index < 0)),
                                        emoji_paging_index, new_possible_index)
            self._emoji_handler.emoji_message_cache_check_not_empty(self._message_cache)
        elif event.char and event.char == '\x01' and event.keycode == 38 and event.keysym == 'a':
            self._message_input_field.select_range(0, 'end')
        return
