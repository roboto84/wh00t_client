# Chat Client Network base class

import os
import emoji
import logging.config
import tkinter as tk
from typing import Callable, Tuple, List
from client_settings import ClientSettings
from client_handlers import ClientHandlers
from wh00t_core.library.client_network import ClientNetwork


class Wh00tClientNetwork(ClientNetwork):
    def __init__(self, logging_object: logging, chat_client_settings: ClientSettings,
                 chat_message: tk.StringVar, chat_client_handlers: ClientHandlers,
                 close_app: Callable[[], None], debug_switch: bool):
        self.logging_object: logging = logging_object
        self.logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging_object.INFO)

        self.client_settings: ClientSettings = chat_client_settings
        self.chat_message: tk.StringVar = chat_message
        self.chat_client_handlers: ClientHandlers = chat_client_handlers
        self.close_app: Callable[[], None] = close_app
        self.debug: bool = debug_switch
        self.client_socket_error = False

        address: Tuple = self.client_settings.get_server_address()
        super().__init__(address[0], address[1], self.client_settings.client_id,
                         self.client_settings.get_client_profile(), self.logging_object)

    def send_wh00t_message(self):
        if self.client_socket_error:
            os._exit(1)
        else:
            try:
                message: str = self.chat_message.get()
                if message.strip() != '':
                    self.chat_client_handlers.message_history_handler(message)
                    if self.chat_client_handlers.emoji_sentence_lock:
                        self.chat_client_handlers.emoji_message_handler(message)
                    elif ((len(message) != 0) and
                          (message not in (self.client_settings.get_exit_command(),
                                           self.client_settings.get_alert_command())) and
                          (message.find(self.client_settings.get_destruct_command()) == -1) and
                          (message[0] == '/') and
                          (message.count('/') == 1)):
                        if message.find('/meme ') >= 0:
                            self.multi_wh00t_message('meme_message',
                                                     self.chat_client_handlers.message_command_handler(message))
                        else:
                            self.chat_client_handlers.message_command_handler(message)
                    else:
                        super().send_message('chat_message', message)
                        if message == self.client_settings.get_exit_command():
                            self.close_app()
            except IOError as io_error:
                self.logger.error(f'Received IOError: {(str(io_error))}')
                self.chat_client_handlers.message_list_push(
                    self.client_settings.client_id,
                    self.chat_client_handlers.get_application_profile_identifier(),
                    self.chat_client_handlers.get_internal_client_category(),
                    self.client_settings.message_time(),
                    '\nDetected remote server disconnect. Shutting down client on next input, check server please.',
                    'local'
                )
                self.client_socket_error = True

    def multi_wh00t_message(self, client_category: str, ascii_array: List[str]):
        try:
            for artLine in ascii_array:
                super().send_message(client_category, artLine)
        except TypeError as type_error:
            self.logger.error(f'Received IOError: {(str(type_error))}')

    def receive_wh00t_message(self) -> None:
        try:
            super().receive(self.received_message_handler)
        except SyntaxError as syntax_error:
            self.logger.error(f'Received SyntaxError: {str(syntax_error)}')
            self.chat_client_handlers.message_list_push(self.client_settings.client_id,
                                                        self.chat_client_handlers.get_application_profile_identifier(),
                                                        self.chat_client_handlers.get_internal_client_category(),
                                                        self.client_settings.message_time(),
                                                        '\nReceived unsupported characters in message',
                                                        'local')

    def received_message_handler(self, package: dict) -> bool:
        if not package:
            self.close_app()
        elif package['message'] == self.client_settings.get_exit_command():
            return False
        else:
            if (package['profile'] != self.chat_client_handlers.get_application_profile_identifier()) or \
                    (package['id'] == self.client_settings.get_server_id()
                     and (package['category'].find('debug') == -1)) \
                    or self.debug:
                emoji_message = emoji.emojize(package['message'], use_aliases=True)
                self._number_of_messages += 1
                self.chat_client_handlers.message_list_push(package['id'], package['profile'], package['category'],
                                                            package['time'], emoji_message, 'network')
            return True
