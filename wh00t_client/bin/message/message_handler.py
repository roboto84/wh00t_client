
import tkinter
import tkinter.font
import webbrowser
import logging
from typing import Optional, List
from threading import Timer
from playsound import playsound
from bin.memes.meme_collection import MemeCollection
from client_settings import ClientSettings
from bin.client.client_helpers import ClientHelpers
from bin.client.client_commands import ClientCommands
from bin.emoji.emoji_handler import EmojiHandler


class MessageHandler:
    def __init__(self, logging_object: logging, client_settings: ClientSettings, message_list: tkinter.Text):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging_object.INFO)
        self._client_settings: ClientSettings = client_settings
        self._message_list: tkinter.Text = message_list
        self._timers: List[Timer] = []
        self._hyperlink_tag_prefix: str = 'hyper-'
        self._internal_client_category: str = 'internal_message'
        self._general_font: tkinter.font = tkinter.font.Font(self._message_list, self._message_list.cget('font'))
        self._client_commands: ClientCommands = ClientCommands(client_settings)
        self._meme_collection: MemeCollection = MemeCollection()

        emoji_font: tkinter.font = tkinter.font.Font(self._message_list, self._message_list.cget('font'))
        brackets_font: tkinter.font = tkinter.font.Font(self._message_list, self._message_list.cget('font'))
        emoji_font.configure(size=client_settings.emoji_font_size)
        brackets_font.configure(size=client_settings.bracket_highlight_font_size, slant='italic')

        self._message_list.tag_configure('Emoji', font=emoji_font, foreground=client_settings.emoji_color)
        self._message_list.tag_configure('Brackets', font=brackets_font,
                                         foreground=client_settings.bracket_highlight_color)
        self._message_list.tag_configure('User_Handle', font=self._general_font,
                                         foreground=client_settings.user_handle_color)
        self._message_list.tag_configure('Other_Users_Handle', font=self._general_font,
                                         foreground=client_settings.other_user_handles_color)
        self._message_list.tag_configure('System', font=self._general_font, foreground=client_settings.system_color)

    def _enter(self, event) -> None:
        self._message_list.config(cursor='hand2')

    def _leave(self, event) -> None:
        self._message_list.config(cursor='')

    def _click(self, event) -> None:
        for tag in self._message_list.tag_names(tkinter.CURRENT):
            if tag[:6] == self._hyperlink_tag_prefix:
                webbrowser.open(self._message_hyperlinks[int(tag[6:])]['link'])
                return

    def _delete_message(self, message: str) -> None:
        count = tkinter.IntVar()
        index = self._message_list.search(message, '1.0', stopindex='end', count=count)
        self._message_list.delete(index, "%s + %sc" % (index, count.get()))

    def _command_message_list_push(self, message: str):
        self.message_list_push(self._client_settings.get_app_title(), self.get_application_profile_identifier(),
                               self.get_internal_client_category(), self._client_settings.message_time(),
                               message, 'local')

    def get_application_profile_identifier(self):
        return self._client_settings.get_app_profile()

    def get_internal_client_category(self):
        return self._internal_client_category

    def close_timers(self):
        for timer in self._timers:
            timer.cancel()

    def message_command_comparator(self, message: str):
        sys = (message in list(self._client_commands.get_system_commands().keys()))
        multi = (any(command in message for command in list(self._client_commands.get_multi_word_commands().keys())))
        return sys or multi

    def message_command_handler(self, message: str) -> Optional[List[str]]:
        if message == '/memes':
            self._command_message_list_push(self._meme_collection.print_memes_help())
        elif '/meme' in message:
            split_message = message.split('/meme', maxsplit=2)
            return self._meme_collection.meme(split_message[1].replace(' ', ''))
        elif message == '/noSound':
            self._client_settings.set_sound_alert_preference(False)
        elif message == '/sound':
            self._client_settings.set_sound_alert_preference(True)
        elif message == '/noNotification':
            self._client_settings.set_notification_alert_preference(False)
        elif message == '/notify':
            self._client_settings.set_notification_alert_preference(True)
        elif message == '/version':
            self._command_message_list_push(f'\n     wh00t client v{self._client_settings.get_client_version()}\n')
        elif message == '/help':
            self._command_message_list_push(self._client_commands.print_help())
        elif message == '/emojis':
            self._command_message_list_push(EmojiHandler.print_emojis_help())

    def _tag_custom_font(self, tag_name, regex, remove_tag_name=None, remove_tag_first=False) -> None:
        count = tkinter.IntVar()
        self._message_list.mark_set('matchStart', '1.0')
        self._message_list.mark_set('matchEnd', '1.0')

        while True:
            index = self._message_list.search(regex, 'matchEnd', 'end', count=count, regexp=True)
            if index == '':
                break  # no match was found

            self._message_list.mark_set('matchStart', index)
            self._message_list.mark_set('matchEnd', '%s+%sc' % (index, count.get()))

            if remove_tag_first:
                self._message_list.tag_remove(remove_tag_name, 'matchStart', 'matchEnd')
            self._message_list.tag_add(tag_name, 'matchStart', 'matchEnd')

    def _tag_hyperlinks(self) -> None:
        self._message_hyperlinks = []
        count = tkinter.IntVar()
        loop_counter = 0
        regex = r'((http|ftp|https)\:\/\/)?([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'

        self._message_list.mark_set('matchStart', '1.0')
        self._message_list.mark_set('matchEnd', '1.0')

        while True:
            start_index = self._message_list.search(regex, 'matchEnd', 'end', count=count, regexp=True)
            end_index = '%s+%sc' % (start_index, count.get())
            if start_index == '':
                break  # no match was found

            self._message_list.mark_set('matchStart', start_index)
            self._message_list.mark_set('matchEnd', end_index)
            hyperlink_tag = f'{self._hyperlink_tag_prefix}%d' % loop_counter

            self._message_hyperlinks.append({
                'start_index': start_index,
                'end_index': end_index,
                'link': self._message_list.get(start_index, end_index),
                'tag': hyperlink_tag
            })

            self._message_list.tag_add(hyperlink_tag, 'matchStart', 'matchEnd')
            self._message_list.tag_bind(hyperlink_tag, "<Button-1>", self._click)
            self._message_list.tag_config(hyperlink_tag, font=self._general_font,
                                          foreground=self._client_settings.system_color, underline=1)
            self._message_list.tag_bind(hyperlink_tag, "<Enter>", self._enter)
            self._message_list.tag_bind(hyperlink_tag, "<Leave>", self._leave)
            self._message_list.tag_bind(hyperlink_tag, "<Button-1>", self._click)
            loop_counter += 1

    def _play_sound_on_message(self, message: str):
        self._client_settings.set_sound_alert_preference(False)
        sound_delayed_action = Timer(5.0, self._client_settings.set_sound_alert_preference, [True])
        sound_delayed_action.start()
        self._timers.append(sound_delayed_action)
        if self._client_settings.get_alert_command() in message:
            playsound(self._client_settings.get_user_alert_sound())
        else:
            playsound(self._client_settings.get_message_sound())

    def _notify_on_message(self, client_id: str, message: str):
        notification = ClientHelpers.notification_formatted_message(client_id, message)
        self._client_settings.set_notification_alert_preference(False)
        notification_delayed_action = Timer(5.0, self._client_settings.set_notification_alert_preference,
                                            [True])
        notification_delayed_action.start()
        self._timers.append(notification_delayed_action)
        if self._client_settings.get_current_platform() == 'Windows':
            win_notify = self._client_settings.get_windows_notifier()
            win_notify.show_toast(self._client_settings.get_app_title(),
                                  notification, threaded=True, duration=3)
        elif self._client_settings.get_current_platform() == 'Linux':
            lin_notify = self._client_settings.get_linux_notifier()
            lin_notify.update(self._client_settings.get_app_title(), notification,
                              self._client_settings.get_app_icon())
            lin_notify.show()

    def message_list_push(self, client_id: str, client_profile: str, client_category: str,
                          message_time: str, message: str, message_type: str) -> None:
        user_handle: str = self._client_settings.client_id
        formatted_message: str = f'| {client_id} ({message_time}) | {message}\n'
        message_is_secret: bool = self._client_settings.get_destruct_command() in formatted_message

        if client_id == self._client_settings.get_server_id():
            formatted_message = f'{message}\n'
        if message_is_secret:
            self_destruct_timer = Timer(60.0, self._delete_message, [formatted_message])
            self_destruct_timer.start()
            self._timers.append(self_destruct_timer)

        self._message_list.insert(tkinter.END, formatted_message)
        self._tag_custom_font('Emoji', r'[\u263a-\U0001f645]')
        self._tag_custom_font('Brackets', r'\[.*\]')
        self._tag_custom_font('Other_Users_Handle', r'\|.*\|')
        self._tag_custom_font('User_Handle', r'\| {}.*\|'.format(user_handle), 'Other_Users_Handle', True)
        self._tag_custom_font('System', r'\~.*\~')
        self._tag_hyperlinks()
        self._message_list.see('end')

        if (message_type != 'local') and (f'| {user_handle} ({message_time}) |' not in formatted_message):
            if self._client_settings.get_sound_alert_preference():
                self._play_sound_on_message(message)
            if not message_is_secret and self._client_settings.get_notification_alert_preference():
                self._notify_on_message(client_id, message)

