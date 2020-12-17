# Chat Client Handlers base class

import tkinter
import tkinter.font
from threading import Thread, Timer
from playsound import playsound
from bin.emojis import Emojis
from bin.help import HelpMenu


class ClientHandlers:
    def __init__(self, client_settings, client_meme_collection, chat_message, message_input_field, message_list):
        self.chat_message = chat_message
        self.message_input_field = message_input_field
        self.client_settings = client_settings
        self.client_meme_collection = client_meme_collection
        self.message_list = message_list

        self.emoji_sentence_lock = False
        self.message_list_message_history = []
        self.message_history_index = 0
        self.user_handle = ''
        self.emoji_dict_keys = list(Emojis.keys())
        self.emoji_paging_index = 0
        self.receive_thread = None
        self.message_cache = None

        emoji_font = tkinter.font.Font(self.message_list, self.message_list.cget('font'))
        brackets_font = tkinter.font.Font(self.message_list, self.message_list.cget('font'))
        general_font = tkinter.font.Font(self.message_list, self.message_list.cget('font'))
        emoji_font.configure(size=client_settings.emoji_font_size)
        brackets_font.configure(size=client_settings.bracket_highlight_font_size, slant='italic')
        self.message_list.tag_configure('Emoji', font=emoji_font, foreground=client_settings.emoji_color)
        self.message_list.tag_configure('Brackets', font=brackets_font,
                                        foreground=client_settings.bracket_highlight_color)
        self.message_list.tag_configure('UserHandle', font=general_font, foreground=client_settings.user_handle_color)
        self.message_list.tag_configure('OtherUsersHandle', font=general_font,
                                        foreground=client_settings.other_user_handles_color)
        self.message_list.tag_configure('System', font=general_font, foreground=client_settings.system_color)

    def thread_it(self, receive):
        self.receive_thread = Thread(target=receive)
        self.receive_thread.start()

    def close_notify(self):
        if self.client_settings.get_current_platform() == 'Linux':
            self.client_settings.linux_notify.uninit()

    def message_command_handler(self, message, number_of_messages, client_socket):
        if message.find('{}'.format('/meme ')) >= 0:
            split_message = message.split('/meme', maxsplit=2)
            self.client_meme_collection.meme(client_socket, split_message[1].replace(' ', ''))
        elif message == '/noSound':
            self.client_settings.set_sound_alert_preference(False)
        elif message == '/sound':
            self.client_settings.set_sound_alert_preference(True)
        elif message == '/noNotification':
            self.client_settings.set_notification_alert_preference(False)
        elif message == '/notify':
            self.client_settings.set_notification_alert_preference(True)
        elif message == '/help':
            self.message_list_push(self.print_help(), 'local', number_of_messages)
        elif message == '/memes':
            self.message_list_push(self.client_meme_collection.print_memes_help(), 'local', number_of_messages)
        elif message == '/emojis':
            self.message_list_push(self.client_meme_collection.print_emojis_help(), 'local', number_of_messages)
        else:
            self.message_list_push('\nCommand not recognized, type /help for list of supported commands', 'local',
                                   number_of_messages)

    @staticmethod
    def message_list_event_handler(event):
        # print(event) # Debug keys
        if event.keycode == 67 and event.keysym == 'c':  # Windows
            return
        elif event.char and event.char == '\x03' and event.keycode == 54 and event.keysym == 'c':  # Linux
            return
        else:
            return 'break'

    def message_history_handler(self, message):
        self.message_list_message_history.append(message)
        if len(self.message_list_message_history) > 10:
            del self.message_list_message_history[0]
        self.message_history_index = len(self.message_list_message_history) - 1
        self.chat_message.set('')

    def emoji_message_cache(self):
        if not self.emoji_sentence_lock and (self.chat_message.get() not in self.emoji_dict_keys):
            self.set_emoji_sentence_lock(True)
            self.message_cache = self.chat_message.get()

    def emoji_message_cache_check_not_empty(self):
        if not self.message_cache.replace(' ', ''):
            self.set_emoji_sentence_lock(False)

    def emoji_message_handler(self, message):
        self.set_emoji_sentence_lock(False)
        self.chat_message.set('{}{}'.format(self.message_cache, message))
        self.message_input_field.icursor(len(self.chat_message.get()))

    def set_emoji_sentence_lock(self, lock_state):
        self.emoji_sentence_lock = lock_state

    def message_entry_event_handler(self, event):
        # print(event) # Debug keys
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

    def tag_custom_font(self, tag_name, regex, remove_tag_name=None, remove_tag_first=False):
        self.message_list.tag_remove(tag_name, '1.0', 'end')

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

    def message_list_push(self, message, message_type, number_of_messages):
        if number_of_messages == 1:
            split_message = message.split()
            self.user_handle = split_message[8].replace('.', '')

        self.message_list.insert(tkinter.END, message)
        self.tag_custom_font('Emoji', r'[\u263a-\U0001f645]')
        self.tag_custom_font('Brackets', r'\[.*\]')
        self.tag_custom_font('OtherUsersHandle', r'\|.*\|')
        self.tag_custom_font('UserHandle', r'\| {}.*\|'.format(self.user_handle), 'OtherUsersHandle', True)
        self.tag_custom_font('System', r'\~.*\~')
        self.message_list.see('end')

        if (message_type != 'local') and (
                message.find('| {} ({}) |'.format(self.user_handle, self.client_settings.message_time())) < 0):
            if self.client_settings.get_sound_alert_preference():
                self.client_settings.set_sound_alert_preference(False)
                sound_delayed_action = Timer(5.0, self.client_settings.set_sound_alert_preference, [True])
                sound_delayed_action.start()
                if message.find('{}'.format(self.client_settings.ALERT_COMMAND)) < 0:
                    playsound(self.client_settings.MESSAGE_SOUND)
                else:
                    playsound(self.client_settings.USER_ALERT_SOUND)
            if self.client_settings.get_notification_alert_preference():
                self.client_settings.set_notification_alert_preference(False)
                notification_delayed_action = Timer(5.0, self.client_settings.set_notification_alert_preference, [True])
                notification_delayed_action.start()
                if self.client_settings.get_current_platform() == 'Windows':
                    win_notify = self.client_settings.get_windows_notifier()
                    win_notify.show_toast('wh00t', 'new message', threaded=True, duration=3)
                elif self.client_settings.get_current_platform() == 'Linux':
                    lin_notify = self.client_settings.get_linux_notifier()
                    lin_notify.update('wh00t', 'new message', self.client_settings.APP_ICON)
                    lin_notify.show()

    @staticmethod
    def print_help():
        client_help = '\n'
        for item in HelpMenu:
            client_help += '\n     {}'.format(item)
        return client_help
