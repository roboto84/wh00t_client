# Chat Client Network base class

import os
import emoji
from socket import AF_INET, socket, SOCK_STREAM


class ClientNetwork:
    def __init__(self, logging_object, chat_client_settings, chat_message, chat_client_handlers):
        self.logger = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging_object.INFO)

        self.client_settings = chat_client_settings
        self.chat_message = chat_message
        self.chat_client_handlers = chat_client_handlers
        self.number_of_messages = 0
        self.client_socket = None
        self.client_socket_error = False
        self.close_app = None

    def sock_it(self):
        try:
            address = self.client_settings.get_server_address()
            self.logger.info(f'Attempting socket connection to {address}')
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(address)
            self.logger.info(f'Connection to {address} has succeeded')
        except ConnectionRefusedError as connection_refused_error:
            self.logger.error(f'Received ConnectionRefusedError: {(str(connection_refused_error))}')
            os._exit(1)
        except OSError as os_error:  # Possibly client has left the chat.
            self.logger.error(f'Received an OSError: {(str(os_error))}')
            os._exit(1)

    def send_message(self, close_app):
        if self.client_socket_error:
            os._exit(1)
        else:
            try:
                message = self.chat_message.get()
                self.chat_client_handlers.message_history_handler(message)
                if self.chat_client_handlers.emoji_sentence_lock:
                    self.chat_client_handlers.emoji_message_handler(message)
                elif ((len(message) != 0) and (message != self.client_settings.EXIT_STRING) and
                      (message != self.client_settings.ALERT_COMMAND) and (message[0] == '/') and (
                              message.count('/') == 1)):
                    self.chat_client_handlers.message_command_handler(message, self.number_of_messages,
                                                                      self.client_socket)
                else:
                    self.client_socket.send(bytes(message, 'utf8'))
                    if message == self.client_settings.EXIT_STRING:
                        close_app()
            except IOError as io_error:
                self.logger.error(f'Received IOError: {(str(io_error))}')
                self.chat_client_handlers.message_list_push('\nDetected remote server disconnect. \
                                    \nShutting down client on next input, check server please.', 'local',
                                                            self.number_of_messages)
                self.client_socket_error = True

    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(self.client_settings.BUFFER_SIZE).decode('utf8', errors='replace')
                emoji_message = emoji.emojize(message, use_aliases=True)
                self.number_of_messages += 1
                if emoji_message == self.client_settings.EXIT_STRING:
                    break
                else:
                    self.chat_client_handlers.message_list_push(emoji_message, 'network', self.number_of_messages)
            except OSError as os_error:  # Possibly client has left the chat.
                self.logger.error(f'Received OSError: {(str(os_error))}')
                break
