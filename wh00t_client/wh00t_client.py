#!/usr/bin/env python3
# wh00t GUI chat client.

import tkinter as tk
import tkinter.font
import os
import ntpath
import logging.config
import webbrowser
from PIL import ImageTk, Image
from dotenv import load_dotenv
from client_settings import ClientSettings
from bin.network.wh00t_client_network import Wh00tClientNetwork
from bin.message.message_history_handler import MessageHistoryHandler
from bin.message.message_handler import MessageHandler
from bin.client.client_helpers import ClientHelpers
from bin.emoji.emoji_handler import EmojiHandler


class Wh00tClient(tk.Tk):
    def __init__(self, logging_object: logging, client_user_name: str, server_address: str,
                 server_port: int, debug_switch: bool):
        super().__init__()
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging_object.INFO)
        self._debug: bool = debug_switch
        self._wh00t_client_settings: ClientSettings = ClientSettings(client_user_name, server_address, server_port)

        # Declare window elements
        self.geometry('{}x{}'.format(
            self._wh00t_client_settings.app_dimensions['width'],
            self._wh00t_client_settings.app_dimensions['height'])
        )
        self.resizable(height=False, width=False)
        self['bg'] = self._wh00t_client_settings.app_background_color

        chat_message: tk.StringVar = tkinter.StringVar()
        chat_frame: tk.Frame = tkinter.Frame(self)
        background_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(
            self._wh00t_client_settings.get_app_banner()))

        banner: tk.Label = tkinter.Label(
            image=background_image,
            bg=self._wh00t_client_settings.background_color,
            highlightbackground=self._wh00t_client_settings.highlight_background_color,
            highlightcolor=self._wh00t_client_settings.highlight_color,
            cursor='hand2'
        )

        message_input_field: tk.Entry = tkinter.Entry(
            self,
            bd=self._wh00t_client_settings.message_entry_border_dimension,
            font=self._wh00t_client_settings.entry_field_font,
            width=self._wh00t_client_settings.message_input_width,
            textvariable=chat_message,
            bg=self._wh00t_client_settings.background_color,
            fg=self._wh00t_client_settings.entry_field_color,
            highlightbackground=self._wh00t_client_settings.highlight_background_color,
            highlightcolor=self._wh00t_client_settings.highlight_color,
            insertbackground=self._wh00t_client_settings.insert_background
        )

        message_list: tk.Text = tkinter.Text(
            chat_frame,
            wrap='word',
            font=self._wh00t_client_settings.message_list_font,
            bd=self._wh00t_client_settings.message_list_border_dimension,
            height=self._wh00t_client_settings.message_list_height,
            width=self._wh00t_client_settings.message_list_width,
            padx=self._wh00t_client_settings.message_list_pad_x,
            pady=self._wh00t_client_settings.message_list_pad_y,
            spacing1=self._wh00t_client_settings.message_list_spacing1,
            bg=self._wh00t_client_settings.background_color,
            fg=self._wh00t_client_settings.font_color,
            highlightbackground=self._wh00t_client_settings.highlight_background_color,
            highlightcolor=self._wh00t_client_settings.highlight_color,
            highlightthickness=self._wh00t_client_settings.message_list_highlight_thickness
        )

        scrollbar: tk.Scrollbar = tkinter.Scrollbar(
            chat_frame,
            bg=self._wh00t_client_settings.background_color,
            activebackground=self._wh00t_client_settings.mouse_over_color,
            command=message_list.yview
        )

        message_list.configure(yscrollcommand=scrollbar.set)

        send_message_button: tk.Button = tkinter.Button(
            self,
            font=self._wh00t_client_settings.button_font,
            bd=1,
            relief=self._wh00t_client_settings.message_submit_button_relief,
            text='🚀 Send',
            height=self._wh00t_client_settings.message_submit_button_height,
            width=self._wh00t_client_settings.message_submit_button_width,
            command=lambda: self._wh00t_client_network.send_wh00t_message(),
            bg=self._wh00t_client_settings.background_color,
            fg=self._wh00t_client_settings.button_color,
            pady=self._wh00t_client_settings.message_submit_button_pad_y,
            activebackground=self._wh00t_client_settings.active_background,
            highlightbackground=self._wh00t_client_settings.highlight_background_color,
            highlightcolor=self._wh00t_client_settings.highlight_color
        )

        self._wh00t_emoji_handler: EmojiHandler = EmojiHandler(chat_message, message_input_field)

        self._wh00t_message_history_handler: MessageHistoryHandler = MessageHistoryHandler(
            logging_object, self._wh00t_client_settings, self._wh00t_emoji_handler,
            chat_message, message_input_field, message_list
        )
        self._wh00t_message_handler: MessageHandler = MessageHandler(
            logging_object, self._wh00t_client_settings, message_list
        )
        self._wh00t_client_network: Wh00tClientNetwork = Wh00tClientNetwork(
            logging_object, self._wh00t_client_settings, chat_message, self._wh00t_message_history_handler,
            self._wh00t_message_handler, self._close_app, self._debug
        )
        self._wh00t_client_helper: ClientHelpers = ClientHelpers(logging_object, self._wh00t_client_settings)

        # Set initial element properties.
        self.title(self._wh00t_client_settings.get_app_title())
        self.protocol('WM_DELETE_WINDOW', lambda: self._on_window_close(chat_message))
        chat_message.set('')
        banner.bind("<1>", lambda e: webbrowser.open('https://github.com/roboto84/wh00t_client'))
        message_list.bind('<Key>', lambda e: self._wh00t_message_history_handler.message_list_event_handler(e))
        message_input_field.bind('<Key>', lambda e: self._wh00t_message_history_handler.message_entry_event_handler(e))
        message_input_field.bind('<Return>', lambda e: self._wh00t_client_network.send_wh00t_message())
        message_input_field.focus()

        # Set elements structure
        banner.grid(row=0, column=1, columnspan=2)
        chat_frame.grid(row=1, column=1, columnspan=2)
        message_list.grid(row=1, column=1)
        scrollbar.grid(row=1, column=2, sticky='ns')
        message_input_field.grid(row=2, column=1, ipady=4, ipadx=4)
        send_message_button.grid(row=2, column=2, pady=10)

        # Initialize and Run App
        try:
            self._wh00t_client_network.sock_it()
            self._wh00t_client_helper.thread_it(self._wh00t_client_network.receive_wh00t_message)
            self.mainloop()
        except KeyboardInterrupt:
            self._logger.warning('Received a KeyboardInterrupt... now exiting')
            self._clean_up()
            os._exit(1)

    def _clean_up(self) -> None:
        self._wh00t_message_handler.close_timers()
        self._wh00t_client_helper.close_notify()
        self._wh00t_client_network.close_it()

    def _close_app(self) -> None:
        if self._wh00t_client_helper.receive_thread.is_alive():
            self.after(50, self._close_app)
        else:
            self._clean_up()
            self.quit()

    def _on_window_close(self, chat_message) -> None:
        if self._wh00t_client_network.client_socket_error:
            self._clean_up()
            os._exit(1)
        else:
            chat_message.set(self._wh00t_client_settings.get_exit_command())
            self._wh00t_client_network.send_wh00t_message()


if __name__ == '__main__':
    HOME_PATH = ntpath.dirname(__file__)
    logging.config.fileConfig(fname=os.path.join(HOME_PATH, 'bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        CLIENT_USER_NAME: str = os.getenv('CLIENT_USER_NAME')
        SERVER_ADDRESS: str = os.getenv('SERVER_ADDRESS')
        SERVER_PORT: int = int(os.getenv('SERVER_PORT'))
        DEBUG = (os.getenv('DEBUG', str('False')).lower() in ("yes", "y", "true", "1", "t"))
        wh00t_client: Wh00tClient = Wh00tClient(logging, CLIENT_USER_NAME, SERVER_ADDRESS, SERVER_PORT, DEBUG)
    except TypeError as type_error:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
