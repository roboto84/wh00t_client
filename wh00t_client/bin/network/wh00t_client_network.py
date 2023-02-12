# Chat Client Network base class

import os
import emoji
import logging.config
import tkinter as tk
from typing import Callable, Tuple, List
from client_settings import ClientSettings
from bin.message.message_handler import MessageHandler
from bin.message.message_history_handler import MessageHistoryHandler
from wh00t_core.library.client_network import ClientNetwork


class Wh00tClientNetwork(ClientNetwork):
    def __init__(self, logging_object: logging, chat_client_settings: ClientSettings,
                 chat_message: tk.StringVar, chat_history_handler: MessageHistoryHandler,
                 chat_message_handler: MessageHandler, close_app: Callable[[], None], debug_switch: bool):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging_object.INFO)
        self._client_settings: ClientSettings = chat_client_settings
        self._chat_message: tk.StringVar = chat_message
        self._chat_history_handler: MessageHistoryHandler = chat_history_handler
        self._chat_message_handler: MessageHandler = chat_message_handler
        self._close_app: Callable[[], None] = close_app
        self._debug: bool = debug_switch
        self.client_socket_error = False
        address: Tuple = self._client_settings.get_server_address()
        super().__init__(address[0], address[1], self._client_settings.client_id,
                         self._client_settings.get_client_profile(), logging_object)

    def send_wh00t_message(self):
        if self.client_socket_error:
            os._exit(1)
        else:
            try:
                message: str = self._chat_message.get()
                if message.strip() != '':
                    self._chat_history_handler.message_history_handler(message)
                    if self._chat_history_handler.get_emoji_sentence_lock():
                        self._chat_history_handler.emoji_message_handler(message)
                    elif self._chat_message_handler.message_command_comparator(message):
                        if '/meme' in message and '/memes' not in message:
                            self.multi_wh00t_message('meme_message',
                                                     self._chat_message_handler.message_command_handler(message))
                        else:
                            self._chat_message_handler.message_command_handler(message)
                    else:
                        super().send_message('chat_message', message, self._client_settings.client_user_name)
                        if message == self._client_settings.get_exit_command():
                            self._close_app()
            except IOError as io_error:
                self._logger.error(f'Received IOError: {(str(io_error))}')
                self._chat_message_handler.message_list_push(
                    self._client_settings.client_id,
                    self._client_settings.client_user_name,
                    self._chat_message_handler.get_application_profile_identifier(),
                    self._chat_message_handler.get_internal_client_category(),
                    self._client_settings.message_time(),
                    '\nDetected remote server disconnect. Shutting down client on next input, check server please.',
                    'local'
                )
                self.client_socket_error = True

    def multi_wh00t_message(self, client_category: str, ascii_array: List[str]):
        try:
            for artLine in ascii_array:
                super().send_message(client_category, artLine, self._client_settings.client_user_name)
        except TypeError as type_error:
            self._logger.error(f'Received IOError: {(str(type_error))}')

    def receive_wh00t_message(self) -> None:
        try:
            super().receive(self.received_message_handler)
        except SyntaxError as syntax_error:
            self._logger.error(f'Received SyntaxError: {str(syntax_error)}')
            self._chat_message_handler.message_list_push(
                self._client_settings.client_id,
                self._client_settings.client_user_name,
                self._chat_message_handler.get_application_profile_identifier(),
                self._chat_message_handler.get_internal_client_category(),
                self._client_settings.message_time(),
                '\nReceived unsupported characters in message',
                'local')

    def _accept_message_comparator(self, package: dict) -> bool:
        bot_profile: str = self._chat_message_handler.get_application_profile_identifier()
        server_id: str = self._client_settings.get_server_id()
        not_a_bot: bool = package['profile'] != bot_profile
        bot_chat_message: bool = (package['profile'] == bot_profile) and (package['category'] == 'chat_message')
        not_server_debug_message: bool = (package['id'] == server_id) and ('debug' not in package['category'])
        client_in_debug_mode: bool = self._debug
        return not_a_bot or bot_chat_message or not_server_debug_message or client_in_debug_mode

    def received_message_handler(self, package: dict) -> bool:
        if not package:
            self._close_app()
        elif package['message'] == self._client_settings.get_exit_command():
            return False
        else:
            if self._accept_message_comparator(package):
                emoji_message = emoji.emojize(package['message'], language='alias')
                self._number_of_messages += 1
                self._chat_message_handler.message_list_push(package['id'], package['username'], package['profile'],
                                                             package['category'], package['time'], emoji_message,
                                                             'network')
            return True
