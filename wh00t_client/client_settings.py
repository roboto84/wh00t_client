# Chat Client base class

import ntpath
import os
import time
import platform
from datetime import datetime
from bin.themes import BaseTheme
from __init__ import __version__


class ClientSettings:
    CLIENT_VERSION = __version__
    CURRENT_PLATFORM = platform.system()
    APP_TITLE = 'wh00t'
    HOME_PATH = ntpath.dirname(__file__)
    APP_BANNER = os.path.join(HOME_PATH, 'assets/visual/banner.png')  # Banner Should be 663w x 90h pixels
    APP_ICON = os.path.join(HOME_PATH, 'assets/visual/icon.png')
    MESSAGE_SOUND = os.path.join(HOME_PATH, 'assets/audio/wh00t7.wav')
    USER_ALERT_SOUND = os.path.join(HOME_PATH, 'assets/audio/AORiver.wav')
    ALERT_COMMAND = '/ao'
    EXIT_STRING = '/exit'

    # Chat Socket
    BUFFER_SIZE = 1024

    def __init__(self, host, port):
        self.server_address = (host, port)
        self.sound_alert_preference = True
        self.notification_alert_preference = True
        self.app_background_color = BaseTheme['app_background_color']
        self.background_color = BaseTheme['background_color']
        self.border_color = BaseTheme['border_color']
        self.button_color = BaseTheme['button_color']
        self.entry_field_color = BaseTheme['entry_field_color']
        self.font_color = BaseTheme['font_color']
        self.mouse_over_color = BaseTheme['mouse_over_color']
        self.highlight_background_color = BaseTheme['highlight_background_color']
        self.highlight_color = BaseTheme['highlight_color']
        self.insert_background = BaseTheme['insert_background']
        self.active_background = BaseTheme['active_background']
        self.emoji_color = BaseTheme['emoji_color']
        self.bracket_highlight_color = BaseTheme['bracket_highlight_color']
        self.user_handle_color = BaseTheme['user_handle_color']
        self.other_user_handles_color = BaseTheme['other_user_handles_color']
        self.system_color = BaseTheme['system_color']

        if self.CURRENT_PLATFORM == 'Windows':
            # import pyglet
            from win10toast import ToastNotifier
            # pyglet.font.add_file('file.ttf')
            self.windows_notification = ToastNotifier()
            self.app_dimensions = {'width': 668, 'height': 420}
            self.message_list_font = ('Calibri', 13)  # Possible future fail safes Veranda, Consolas
            self.entry_field_font = ('Calibri', 17)
            self.button_font = ('Calibri', 13)
            self.emoji_font_size = 32
            self.bracket_highlight_font_size = 16
            self.message_list_width = 70
            self.message_input_width = 45
            self.message_list_highlight_thickness = 8
            self.message_list_spacing1 = 1
            self.message_list_pad_x = 1
            self.message_list_pad_y = 1
            self.message_entry_border_dimension = 1
            self.message_submit_button_height = 1
            self.message_submit_button_pad_y = 4
            self.message_list_border_dimension = 2
            self.message_submit_button_relief = 'ridge'

        elif self.CURRENT_PLATFORM == 'Linux':
            import gi
            gi.require_version('Notify', '0.7')
            from gi.repository import Notify
            self.linux_notify = Notify
            self.linux_notify.init(self.APP_TITLE)
            self.linux_notification = self.linux_notify.Notification.new("messageAlert")
            self.app_dimensions = {'width': 665, 'height': 435}
            self.message_list_font = ('DejaVu Sans', 12)
            self.entry_field_font = ('DejaVu Sans', 15)
            self.button_font = ('DejaVu Sans', 12)
            self.emoji_font_size = 30
            self.bracket_highlight_font_size = 15
            self.message_list_width = 63
            self.message_input_width = 40
            self.message_list_highlight_thickness = 6
            self.message_list_spacing1 = 5
            self.message_list_pad_x = 5
            self.message_list_pad_y = 7
            self.message_entry_border_dimension = 0
            self.message_submit_button_height = 1
            self.message_submit_button_pad_y = 5
            self.message_list_border_dimension = 0
            self.message_submit_button_relief = 'flat'

    def get_server_address(self):
        return self.server_address

    def set_sound_alert_preference(self, state):
        self.sound_alert_preference = state

    def set_notification_alert_preference(self, state):
        self.notification_alert_preference = state

    def get_notification_alert_preference(self):
        return self.notification_alert_preference

    def get_sound_alert_preference(self):
        return self.sound_alert_preference

    def get_current_platform(self):
        return self.CURRENT_PLATFORM

    def get_linux_notifier(self):
        return self.linux_notification

    def get_windows_notifier(self):
        return self.windows_notification

    @staticmethod
    def message_time():
        return datetime.fromtimestamp(time.time()).strftime('%m/%d %H:%M')
