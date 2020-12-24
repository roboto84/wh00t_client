#!/usr/bin/env python3
# wh00t GUI chat client.

import tkinter as tk
import tkinter.font
import os
import ntpath
import logging.config
from PIL import ImageTk, Image
from dotenv import load_dotenv
from client_settings import ClientSettings
from client_network import ClientNetwork
from client_handlers import ClientHandlers
from meme_collection import MemeCollection


class Wh00tClient(tk.Tk):
    def __init__(self, logging_object, server_address, server_port):
        super().__init__()
        self.wh00t_client_settings = ClientSettings(server_address, server_port)
        self.wh00t_client_meme_collection = MemeCollection()

        # Declare window elements
        self.geometry('{}x{}'.format(self.wh00t_client_settings.app_dimensions['width'],
                                     self.wh00t_client_settings.app_dimensions['height']))
        self.resizable(height=False, width=False)
        self['bg'] = self.wh00t_client_settings.app_background_color

        chat_message = tkinter.StringVar()
        chat_frame = tkinter.Frame(self)
        background_image = ImageTk.PhotoImage(Image.open(self.wh00t_client_settings.APP_BANNER))

        banner = tkinter.Label(image=background_image,
                               bg=self.wh00t_client_settings.background_color,
                               highlightbackground=self.wh00t_client_settings.highlight_background_color,
                               highlightcolor=self.wh00t_client_settings.highlight_color)

        message_input_field = tkinter.Entry(self,
                                            bd=self.wh00t_client_settings.message_entry_border_dimension,
                                            font=self.wh00t_client_settings.entry_field_font,
                                            width=self.wh00t_client_settings.message_input_width,
                                            textvariable=chat_message, bg=self.wh00t_client_settings.background_color,
                                            fg=self.wh00t_client_settings.entry_field_color,
                                            highlightbackground=self.wh00t_client_settings.highlight_background_color,
                                            highlightcolor=self.wh00t_client_settings.highlight_color,
                                            insertbackground=self.wh00t_client_settings.insert_background)

        message_list = tkinter.Text(chat_frame,
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
                                    highlightthickness=self.wh00t_client_settings.message_list_highlight_thickness)

        scrollbar = tkinter.Scrollbar(chat_frame,
                                      bg=self.wh00t_client_settings.background_color,
                                      activebackground=self.wh00t_client_settings.mouse_over_color,
                                      command=message_list.yview)

        message_list.configure(yscrollcommand=scrollbar.set)

        send_message_button = tkinter.Button(self,
                                             font=self.wh00t_client_settings.button_font,
                                             bd=1,
                                             relief=self.wh00t_client_settings.message_submit_button_relief,
                                             text='📨 Send',
                                             height=self.wh00t_client_settings.message_submit_button_height,
                                             width=8,
                                             command=lambda: self.wh00t_client_network.send_message(self.close_app),
                                             bg=self.wh00t_client_settings.background_color,
                                             fg=self.wh00t_client_settings.button_color,
                                             pady=self.wh00t_client_settings.message_submit_button_pad_y,
                                             activebackground=self.wh00t_client_settings.active_background,
                                             highlightbackground=self.wh00t_client_settings.highlight_background_color,
                                             highlightcolor=self.wh00t_client_settings.highlight_color)

        self.wh00t_client_handlers = ClientHandlers(logging_object, self.wh00t_client_settings,
                                                    self.wh00t_client_meme_collection, chat_message,
                                                    message_input_field, message_list)
        self.wh00t_client_network = ClientNetwork(logging_object, self.wh00t_client_settings, chat_message,
                                                  self.wh00t_client_handlers)

        # Set initial element properties.
        self.title(self.wh00t_client_settings.APP_TITLE)
        self.protocol('WM_DELETE_WINDOW', lambda: self.on_window_close(chat_message))
        chat_message.set('')
        message_list.bind('<Key>', lambda e: self.wh00t_client_handlers.message_list_event_handler(e))
        message_input_field.bind('<Key>', lambda e: self.wh00t_client_handlers.message_entry_event_handler(e))
        message_input_field.bind('<Return>', lambda e: self.wh00t_client_network.send_message(self.close_app))
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
        self.wh00t_client_handlers.thread_it(self.wh00t_client_network.receive)
        self.mainloop()

    def close_app(self):
        if self.wh00t_client_handlers.receive_thread.is_alive():
            self.after(50, self.close_app)
        else:
            self.wh00t_client_handlers.close_notify()
            self.wh00t_client_network.client_socket.close()
            self.quit()

    def on_window_close(self, chat_message):
        if self.wh00t_client_network.client_socket_error:
            os._exit(1)
        else:
            chat_message.set(self.wh00t_client_settings.EXIT_STRING)
            self.wh00t_client_network.send_message(self.close_app)


if __name__ == '__main__':
    HOME_PATH = ntpath.dirname(__file__)
    logging.config.fileConfig(fname=os.path.join(HOME_PATH, 'bin/logging.conf'), disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
        SERVER_PORT = int(os.getenv('SERVER_PORT'))
        wh00t_client = Wh00tClient(logging, SERVER_ADDRESS, SERVER_PORT)
    except TypeError as type_error:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
