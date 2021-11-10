# Chat Client Handlers base class
import logging
import tkinter
import tkinter.font
import webbrowser
from meme_collection import MemeCollection
from client_settings import ClientSettings
from typing import Optional, List, Callable
from threading import Thread, Timer
from playsound import playsound
from bin.emojis import Emojis
from bin.help import HelpMenu


class ClientHandlers:
    def __init__(self, logging_object, client_settings, client_meme_collection, chat_message: tkinter.StringVar,
                 message_input_field, message_list):
        self.logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging_object.INFO)

        self.chat_message: tkinter.StringVar = chat_message
        self.message_input_field: tkinter.Entry = message_input_field
        self.client_settings: ClientSettings = client_settings
        self.client_meme_collection: MemeCollection = client_meme_collection
        self.message_list: tkinter.Text = message_list

        self.emoji_sentence_lock: bool = False
        self.message_list_message_history: List[str] = []
        self.message_history_index: int = 0
        self.user_handle: str = self.client_settings.client_id
        self.emoji_dict_keys: List[str] = list(Emojis.keys())
        self.emoji_paging_index: int = 0
        self.receive_thread: Optional[Thread] = None
        self.message_cache: Optional[str] = None
        self.message_hyperlinks: List[dict] = []

        self.general_font: tkinter.font = tkinter.font.Font(self.message_list, self.message_list.cget('font'))
        emoji_font: tkinter.font = tkinter.font.Font(self.message_list, self.message_list.cget('font'))
        brackets_font: tkinter.font = tkinter.font.Font(self.message_list, self.message_list.cget('font'))

        emoji_font.configure(size=client_settings.emoji_font_size)
        brackets_font.configure(size=client_settings.bracket_highlight_font_size, slant='italic')

        self.message_list.tag_configure('Emoji', font=emoji_font, foreground=client_settings.emoji_color)
        self.message_list.tag_configure('Brackets', font=brackets_font,
                                        foreground=client_settings.bracket_highlight_color)
        self.message_list.tag_configure('UserHandle', font=self.general_font,
                                        foreground=client_settings.user_handle_color)
        self.message_list.tag_configure('OtherUsersHandle', font=self.general_font,
                                        foreground=client_settings.other_user_handles_color)
        self.message_list.tag_configure('System', font=self.general_font, foreground=client_settings.system_color)

    def _enter(self, event) -> None:
        self.message_list.config(cursor='hand2')

    def _leave(self, event) -> None:
        self.message_list.config(cursor='')

    def _click(self, event) -> None:
        for tag in self.message_list.tag_names(tkinter.CURRENT):
            if tag[:6] == 'hyper-':
                webbrowser.open(self.message_hyperlinks[int(tag[6:])]['link'])
                return

    def thread_it(self, socket_receive: Callable[[], None]) -> None:
        self.receive_thread = Thread(target=socket_receive)
        self.receive_thread.start()

    def close_notify(self) -> None:
        if self.client_settings.get_current_platform() == 'Linux':
            self.client_settings.linux_notify.uninit()

    def message_command_handler(self, message: str) -> Optional[List[str]]:
        if message.find('/meme ') >= 0:
            split_message = message.split('/meme', maxsplit=2)
            return self.client_meme_collection.meme(split_message[1].replace(' ', ''))
        elif message == '/noSound':
            self.client_settings.set_sound_alert_preference(False)
        elif message == '/sound':
            self.client_settings.set_sound_alert_preference(True)
        elif message == '/noNotification':
            self.client_settings.set_notification_alert_preference(False)
        elif message == '/notify':
            self.client_settings.set_notification_alert_preference(True)
        elif message == '/version':
            self.message_list_push('wh00t', 'app', 'internal_message', self.client_settings.message_time(),
                                   f'\n     wh00t client v{self.client_settings.CLIENT_VERSION}\n', 'local')
        elif message == '/help':
            self.message_list_push('wh00t', 'app', 'internal_message', self.client_settings.message_time(),
                                   self.print_help(), 'local')
        elif message == '/memes':
            self.message_list_push('wh00t', 'app', 'internal_message', self.client_settings.message_time(),
                                   self.client_meme_collection.print_memes_help(), 'local')
        elif message == '/emojis':
            self.message_list_push('wh00t', 'app', 'internal_message', self.client_settings.message_time(),
                                   self.client_meme_collection.print_emojis_help(), 'local')
        else:
            self.message_list_push('wh00t', 'app', 'internal_message', self.client_settings.message_time(),
                                   '\nCommand not recognized, type /help for list of supported commands\n', 'local')

    def message_list_event_handler(self, event) -> Optional[str]:
        self.logger.debug(str(event))
        if event.keycode == 67 and event.keysym == 'c':  # Windows
            return
        elif event.char and event.char == '\x03' and event.keycode == 54 and event.keysym == 'c':  # Linux
            return
        else:
            return 'break'

    def message_history_handler(self, message: str) -> None:
        self.message_list_message_history.append(message)
        if len(self.message_list_message_history) > 10:
            del self.message_list_message_history[0]
        self.message_history_index = len(self.message_list_message_history) - 1
        self.chat_message.set('')

    def emoji_message_cache(self) -> None:
        if not self.emoji_sentence_lock and (self.chat_message.get() not in self.emoji_dict_keys):
            self.set_emoji_sentence_lock(True)
            self.message_cache = self.chat_message.get()

    def emoji_message_cache_check_not_empty(self) -> None:
        if not self.message_cache.replace(' ', ''):
            self.set_emoji_sentence_lock(False)

    def emoji_message_handler(self, message: str) -> None:
        self.set_emoji_sentence_lock(False)
        self.chat_message.set(f'{self.message_cache}{message}')
        self.message_input_field.icursor(len(self.chat_message.get()))

    def set_emoji_sentence_lock(self, lock_state: bool) -> None:
        self.emoji_sentence_lock = lock_state

    def message_entry_event_handler(self, event) -> None:
        self.logger.debug(str(event))
        if event.keysym == 'Escape':
            if self.emoji_sentence_lock:
                self.chat_message.set(self.message_cache)
                self.emoji_sentence_lock = False
            else:
                self.chat_message.set(self.client_settings.EXIT_STRING)
            self.message_input_field.icursor(len(self.chat_message.get()))
        elif event.keysym == 'Up':
            if self.message_history_index < 0:
                self.message_history_index = len(self.message_list_message_history) - 1
            if len(self.message_list_message_history) != 0:
                self.chat_message.set(self.message_list_message_history[self.message_history_index])
                self.message_input_field.icursor(len(self.chat_message.get()))
                self.message_history_index -= 1
        elif event.keysym == 'Down':
            self.emoji_paging_index = 0
            self.message_history_index = len(self.message_list_message_history) - 1
            self.chat_message.set('')
            self.message_cache = ''
        elif (event.keysym == 'Prior') or (event.keysym == 'Next'):
            self.emoji_message_cache()
            if event.keysym == 'Prior':
                self.emoji_paging_index += 1
                if self.emoji_paging_index > len(self.emoji_dict_keys) - 1:
                    self.emoji_paging_index = 0
                self.chat_message.set(self.emoji_dict_keys[self.emoji_paging_index])
                self.message_input_field.icursor(len(self.chat_message.get()))
            elif event.keysym == 'Next':
                self.emoji_paging_index -= 1
                if self.emoji_paging_index < 0:
                    self.emoji_paging_index = len(self.emoji_dict_keys) - 1
                self.chat_message.set(self.emoji_dict_keys[self.emoji_paging_index])
                self.message_input_field.icursor(len(self.chat_message.get()))
            self.emoji_message_cache_check_not_empty()
        elif event.char and event.char == '\x01' and event.keycode == 38 and event.keysym == 'a':
            self.message_input_field.select_range(0, 'end')
        return

    def tag_hyperlinks(self) -> None:
        self.message_hyperlinks = []
        count = tkinter.IntVar()
        loop_counter = 0
        regex = r'((http|ftp|https)\:\/\/)?([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'

        self.message_list.mark_set('matchStart', '1.0')
        self.message_list.mark_set('matchEnd', '1.0')

        while True:
            start_index = self.message_list.search(regex, 'matchEnd', 'end', count=count, regexp=True)
            end_index = '%s+%sc' % (start_index, count.get())
            if start_index == '':
                break  # no match was found

            self.message_list.mark_set('matchStart', start_index)
            self.message_list.mark_set('matchEnd', end_index)
            hyperlink_tag = "hyper-%d" % loop_counter

            self.message_hyperlinks.append({
                'start_index': start_index,
                'end_index': end_index,
                'link': self.message_list.get(start_index, end_index),
                'tag': hyperlink_tag
            })

            self.message_list.tag_add(hyperlink_tag, 'matchStart', 'matchEnd')
            self.message_list.tag_bind(hyperlink_tag, "<Button-1>", self._click)
            self.message_list.tag_config(hyperlink_tag, font=self.general_font,
                                         foreground=self.client_settings.system_color, underline=1)
            self.message_list.tag_bind(hyperlink_tag, "<Enter>", self._enter)
            self.message_list.tag_bind(hyperlink_tag, "<Leave>", self._leave)
            self.message_list.tag_bind(hyperlink_tag, "<Button-1>", self._click)
            loop_counter += 1

    def tag_custom_font(self, tag_name, regex, remove_tag_name=None, remove_tag_first=False) -> None:
        count = tkinter.IntVar()
        self.message_list.mark_set('matchStart', '1.0')
        self.message_list.mark_set('matchEnd', '1.0')

        while True:
            index = self.message_list.search(regex, 'matchEnd', 'end', count=count, regexp=True)
            if index == '':
                break  # no match was found

            self.message_list.mark_set('matchStart', index)
            self.message_list.mark_set('matchEnd', '%s+%sc' % (index, count.get()))

            if remove_tag_first:
                self.message_list.tag_remove(remove_tag_name, 'matchStart', 'matchEnd')
            self.message_list.tag_add(tag_name, 'matchStart', 'matchEnd')

    @staticmethod
    def notification_formatted_message(client_id: str, message: str) -> str:
        notification_formatted_message = f'{client_id}: {message}'
        if len(message) > 58:
            notification_substr = notification_formatted_message[0:57]
            return f'{notification_substr}...'
        else:
            return notification_formatted_message

    def message_list_push(self, client_id: str, client_profile: str, client_category: str,
                          message_time: str, message: str, message_type: str) -> None:
        formatted_message = f'| {client_id} ({message_time}) | {message}\n'
        notification = self.notification_formatted_message(client_id, message)

        if client_profile == 'app':
            formatted_message = f'{message}\n'
        self.message_list.insert(tkinter.END, formatted_message)
        self.tag_custom_font('Emoji', r'[\u263a-\U0001f645]')
        self.tag_custom_font('Brackets', r'\[.*\]')
        self.tag_custom_font('OtherUsersHandle', r'\|.*\|')
        self.tag_custom_font('UserHandle', r'\| {}.*\|'.format(self.user_handle), 'OtherUsersHandle', True)
        self.tag_custom_font('System', r'\~.*\~')
        self.tag_hyperlinks()
        self.message_list.see('end')

        if (message_type != 'local') and (formatted_message.find(f'| {self.user_handle} ({message_time}) |') < 0):
            if self.client_settings.get_sound_alert_preference():
                self.client_settings.set_sound_alert_preference(False)
                sound_delayed_action = Timer(5.0, self.client_settings.set_sound_alert_preference, [True])
                sound_delayed_action.start()
                if message.find(f'{self.client_settings.ALERT_COMMAND}') < 0:
                    playsound(self.client_settings.MESSAGE_SOUND)
                else:
                    playsound(self.client_settings.USER_ALERT_SOUND)
            if self.client_settings.get_notification_alert_preference():
                self.client_settings.set_notification_alert_preference(False)
                notification_delayed_action = Timer(5.0, self.client_settings.set_notification_alert_preference, [True])
                notification_delayed_action.start()
                if self.client_settings.get_current_platform() == 'Windows':
                    win_notify = self.client_settings.get_windows_notifier()
                    win_notify.show_toast('wh00t', notification, threaded=True, duration=3)
                elif self.client_settings.get_current_platform() == 'Linux':
                    lin_notify = self.client_settings.get_linux_notifier()
                    lin_notify.update('wh00t', notification, self.client_settings.APP_ICON)
                    lin_notify.show()

    @staticmethod
    def print_help() -> str:
        client_help = '\n'
        for item in HelpMenu:
            client_help += f'\n     {item}'
        return f'{client_help}\n'
