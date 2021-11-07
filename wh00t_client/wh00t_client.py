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
from wh00t_client_network import Wh00tClientNetwork
from client_handlers import ClientHandlers
from meme_collection import MemeCollection


class Wh00tClient(tk.Tk):
    def __init__(self, logging_object: logging, client_user_name: str, server_address: str, server_port: int,
                 debug_switch: bool):
        super().__init__()
        self.debug: bool = debug_switch
        self.wh00t_client_settings: ClientSettings = ClientSettings(client_user_name, server_address, server_port)
        self.wh00t_client_meme_collection: MemeCollection = MemeCollection()

        # Declare window elements
        self.geometry('{}x{}'.format(
            self.wh00t_client_settings.app_dimensions['width'],
            self.wh00t_client_settings.app_dimensions['height'])
        )
        self.resizable(height=False, width=False)
        self['bg'] = self.wh00t_client_settings.app_background_color

        chat_message: tk.StringVar = tkinter.StringVar()
        chat_frame: tk.Frame = tkinter.Frame(self)
        background_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(self.wh00t_client_settings.APP_BANNER))

        banner: tk.Label = tkinter.Label(
            image=background_image,
            bg=self.wh00t_client_settings.background_color,
            highlightbackground=self.wh00t_client_settings.highlight_background_color,
            highlightcolor=self.wh00t_client_settings.highlight_color,
            cursor='hand2'
        )

        message_input_field: tk.Entry = tkinter.Entry(
            self,
            bd=self.wh00t_client_settings.message_entry_border_dimension,
            font=self.wh00t_client_settings.entry_field_font,
            width=self.wh00t_client_settings.message_input_width,
            textvariable=chat_message,
            bg=self.wh00t_client_settings.background_color,
            fg=self.wh00t_client_settings.entry_field_color,
            highlightbackground=self.wh00t_client_settings.highlight_background_color,
            highlightcolor=self.wh00t_client_settings.highlight_color,
            insertbackground=self.wh00t_client_settings.insert_background
        )

        message_list: tk.Text = tkinter.Text(
            chat_frame,
            wrap='word',
            font=self.wh00t_client_settings.message_list_font,
            bd=self.wh00t_client_settings.message_list_border_dimension,
            height=11,
            width=self.wh00t_client_settings.message_list_width,
            padx=self.wh00t_client_settings.message_list_pad_x,
            pady=self.wh00t_client_settings.message_list_pad_y,
            spacing1=self.wh00t_client_settings.message_list_spacing1,
            bg=self.wh00t_client_settings.background_color,
            fg=self.wh00t_client_settings.font_color,
            highlightbackground=self.wh00t_client_settings.highlight_background_color,
            highlightcolor=self.wh00t_client_settings.highlight_color,
            highlightthickness=self.wh00t_client_settings.message_list_highlight_thickness
        )

        scrollbar: tk.Scrollbar = tkinter.Scrollbar(
            chat_frame,
            bg=self.wh00t_client_settings.background_color,
            activebackground=self.wh00t_client_settings.mouse_over_color,
            command=message_list.yview
        )

        message_list.configure(yscrollcommand=scrollbar.set)

        send_message_button: tk.Button = tkinter.Button(
            self,
            font=self.wh00t_client_settings.button_font,
            bd=1,
            relief=self.wh00t_client_settings.message_submit_button_relief,
            text='🚀 Send',
            height=self.wh00t_client_settings.message_submit_button_height,
            width=8,
            command=lambda: self.wh00t_client_network.send_wh00t_message(),
            bg=self.wh00t_client_settings.background_color,
            fg=self.wh00t_client_settings.button_color,
            pady=self.wh00t_client_settings.message_submit_button_pad_y,
            activebackground=self.wh00t_client_settings.active_background,
            highlightbackground=self.wh00t_client_settings.highlight_background_color,
            highlightcolor=self.wh00t_client_settings.highlight_color
        )

        self.wh00t_client_handlers: ClientHandlers = ClientHandlers(
            logging_object, self.wh00t_client_settings,
            self.wh00t_client_meme_collection, chat_message,
            message_input_field, message_list
        )
        self.wh00t_client_network: Wh00tClientNetwork = Wh00tClientNetwork(
            logging_object, self.wh00t_client_settings, chat_message,
            self.wh00t_client_handlers, self.close_app, self.debug
        )

        # Set initial element properties.
        self.title(self.wh00t_client_settings.APP_TITLE)
        self.protocol('WM_DELETE_WINDOW', lambda: self.on_window_close(chat_message))
        chat_message.set('')
        banner.bind("<1>", lambda e: webbrowser.open('https://github.com/roboto84/wh00t_client'))
        message_list.bind('<Key>', lambda e: self.wh00t_client_handlers.message_list_event_handler(e))
        message_input_field.bind('<Key>', lambda e: self.wh00t_client_handlers.message_entry_event_handler(e))
        message_input_field.bind('<Return>', lambda e: self.wh00t_client_network.send_wh00t_message())
        message_input_field.focus()

        # Set elements structure
        banner.grid(row=0, column=1, columnspan=2)
        chat_frame.grid(row=1, column=1, columnspan=2)
        message_list.grid(row=1, column=1)
        scrollbar.grid(row=1, column=2, sticky='ns')
        message_input_field.grid(row=2, column=1, ipady=4, ipadx=4)
        send_message_button.grid(row=2, column=2, pady=10)

        # Initialize and Run App
        self.wh00t_client_network.sock_it()
        self.wh00t_client_handlers.thread_it(self.wh00t_client_network.receive_wh00t_message)
        self.mainloop()

    def close_app(self) -> None:
        if self.wh00t_client_handlers.receive_thread.is_alive():
            self.after(50, self.close_app)
        else:
            self.wh00t_client_handlers.close_notify()
            self.wh00t_client_network.close_it()
            self.quit()

    def on_window_close(self, chat_message) -> None:
        if self.wh00t_client_network.client_socket_error:
            os._exit(1)
        else:
            chat_message.set(self.wh00t_client_settings.EXIT_STRING)
            self.wh00t_client_network.send_wh00t_message()


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
