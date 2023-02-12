# Chat Client base class

import ntpath
import os
import time
import platform
from typing import Tuple, Literal
from datetime import datetime
from bin.themes.themes import BaseTheme
from __init__ import __version__
from wh00t_core.library.network_commons import NetworkCommons


class ClientSettings:
    _CLIENT_VERSION: str = __version__
    _CURRENT_PLATFORM: str = platform.system()
    _APP_TITLE: str = 'wh00t'
    _HOME_PATH: str = ntpath.dirname(__file__)
    _APP_BANNER: str = os.path.join(_HOME_PATH, 'assets/visual/banner.png')  # Banner Should be 663w x 90h pixels
    _APP_ICON: str = os.path.join(_HOME_PATH, 'assets/visual/icon.png')
    _MESSAGE_SOUND: str = os.path.join(_HOME_PATH, 'assets/audio/wh00t7.wav')
    _USER_ALERT_SOUND: str = os.path.join(_HOME_PATH, 'assets/audio/AORiver.wav')
    _ALERT_COMMAND: str = '/ao'
    _network_commons: NetworkCommons = NetworkCommons()

    def __init__(self, client_user_name: str, host: str, port: int):
        self.client_id: str = 'wh00t_client'
        self.client_user_name: str = client_user_name
        self.server_address: Tuple = (host, port)
        self.sound_alert_preference: bool = True
        self.notification_alert_preference: bool = True
        self.app_background_color: str = BaseTheme['app_background_color']
        self.background_color: str = BaseTheme['background_color']
        self.border_color: str = BaseTheme['border_color']
        self.button_color: str = BaseTheme['button_color']
        self.entry_field_color: str = BaseTheme['entry_field_color']
        self.font_color: str = BaseTheme['font_color']
        self.mouse_over_color: str = BaseTheme['mouse_over_color']
        self.highlight_background_color: str = BaseTheme['highlight_background_color']
        self.highlight_color: str = BaseTheme['highlight_color']
        self.insert_background: str = BaseTheme['insert_background']
        self.active_background: str = BaseTheme['active_background']
        self.emoji_color: str = BaseTheme['emoji_color']
        self.bracket_highlight_color: str = BaseTheme['bracket_highlight_color']
        self.user_handle_color: str = BaseTheme['user_handle_color']
        self.other_user_handles_color: str = BaseTheme['other_user_handles_color']
        self.system_color: str = BaseTheme['system_color']

        if self._CURRENT_PLATFORM == 'Windows':
            # import pyglet
            from win10toast import ToastNotifier
            # pyglet.font.add_file('file.ttf')
            self.windows_notification: ToastNotifier = ToastNotifier()
            self.app_dimensions: dict = {'width': 668, 'height': 420}
            self.message_list_font: Tuple = ('Calibri', 13)  # Possible future fail safes Veranda, Consolas
            self.entry_field_font: Tuple = ('Calibri', 17)
            self.button_font: Tuple = ('Calibri', 13)
            self.emoji_font_size: int = 32
            self.bracket_highlight_font_size: int = 16
            self.message_list_width: int = 70
            self.message_list_height: int = 11
            self.message_input_width: int = 45
            self.message_list_highlight_thickness: int = 8
            self.message_list_spacing1: int = 1
            self.message_list_pad_x: int = 1
            self.message_list_pad_y: int = 1
            self.message_entry_border_dimension: int = 1
            self.message_submit_button_height: int = 1
            self.message_submit_button_width: int = 8
            self.message_submit_button_pad_y: int = 4
            self.message_list_border_dimension: int = 2
            self.message_submit_button_relief: Literal['ridge'] = 'ridge'

        elif self._CURRENT_PLATFORM == 'Linux':
            import gi
            gi.require_version('Notify', '0.7')
            from gi.repository import Notify
            self.linux_notify: Notify = Notify
            self.linux_notify.init(self._APP_TITLE)
            self.linux_notification = self.linux_notify.Notification.new("messageAlert")
            self.app_dimensions: dict = {'width': 665, 'height': 435}
            self.message_list_font: Tuple = ('DejaVu Sans', 12)
            self.entry_field_font: Tuple = ('DejaVu Sans', 15)
            self.button_font: Tuple = ('DejaVu Sans', 13)
            self.emoji_font_size: int = 30
            self.bracket_highlight_font_size: int = 15
            self.message_list_width: int = 63
            self.message_list_height: int = 11
            self.message_input_width: int = 40
            self.message_list_highlight_thickness: int = 6
            self.message_list_spacing1: int = 5
            self.message_list_pad_x: int = 5
            self.message_list_pad_y: int = 7
            self.message_entry_border_dimension: int = 0
            self.message_submit_button_height: int = 0
            self.message_submit_button_width: int = 8
            self.message_submit_button_pad_y: int = 4
            self.message_list_border_dimension: int = 0
            self.message_submit_button_relief: Literal['flat'] = 'flat'

    def get_server_address(self) -> Tuple:
        return self.server_address

    def set_sound_alert_preference(self, state) -> None:
        self.sound_alert_preference = state

    def set_notification_alert_preference(self, state) -> None:
        self.notification_alert_preference = state

    def get_notification_alert_preference(self) -> bool:
        return self.notification_alert_preference

    def get_sound_alert_preference(self) -> bool:
        return self.sound_alert_preference

    def get_current_platform(self) -> str:
        return self._CURRENT_PLATFORM

    def get_linux_notifier(self):
        return self.linux_notification

    def get_windows_notifier(self):
        return self.windows_notification

    def get_client_version(self):
        return self._CLIENT_VERSION

    def get_app_title(self):
        return self._APP_TITLE

    def get_app_banner(self):
        return self._APP_BANNER

    def get_app_icon(self):
        return self._APP_ICON

    def get_message_sound(self):
        return self._MESSAGE_SOUND

    def get_user_alert_sound(self):
        return self._USER_ALERT_SOUND

    def get_alert_command(self):
        return self._ALERT_COMMAND

    def get_exit_command(self):
        return self._network_commons.get_exit_command()

    def get_destruct_command(self):
        return self._network_commons.get_destruct_command()

    def get_app_profile(self):
        return self._network_commons.get_app_profile()

    def get_client_profile(self):
        return self._network_commons.get_user_profile()

    def get_server_id(self):
        return self._network_commons.get_server_id()

    @staticmethod
    def message_time() -> str:
        return datetime.fromtimestamp(time.time()).strftime('%m/%d %H:%M')
