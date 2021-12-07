# Chat Client Help Menus Text
from client_settings import ClientSettings


class ClientCommands:
    def __init__(self, client_settings: ClientSettings):
        self._system_commands: dict = {
            '/help': '- prints this help summary',
            '/version': '- turn notification sounds on',
            '/sound': '- turn notification sounds on',
            '/noSound': '- turn notification sounds off',
            '/notify': '- turn notification toast on',
            '/noNotification': '- turn notification toast off',
            '/emojis': '- print list of page up/down supported emojis',
            '/memes': '- prints out a list of available meme commands',
        }
        self._multi_word_commands: dict = {
            '/meme': '{memeName} - sends specific meme as a message. See /memes',
        }
        self._network_commands = {
            client_settings.get_exit_command(): '- exit wh00t client',
            client_settings.get_destruct_command(): '{secret message} - self destruct secret message in 60 sec',
            client_settings.get_alert_command(): '- send a vocal sound alert to chat, currently "A-O River!" '
                                                 'from https://www.youtube.com/watch?v=FtLbndaobhw',
        }
        self._system_keywords = {**self._system_commands, **self._network_commands, **self._multi_word_commands}

        self._system_commands = dict(sorted(self._system_commands.items()))
        self._multi_word_commands = dict(sorted(self._multi_word_commands.items()))
        self._network_commands = dict(sorted(self._network_commands.items()))
        self._system_keywords = dict(sorted(self._system_keywords.items()))

    def get_system_commands(self) -> dict:
        return self._system_commands

    def get_network_commands(self) -> dict:
        return self._network_commands

    def get_multi_word_commands(self) -> dict:
        return self._multi_word_commands

    def get_system_keywords(self) -> dict:
        return self._system_keywords

    def print_help(self) -> str:
        client_help = '\n'
        for key, value in self._system_keywords.items():
            client_help += f'\n     {key} {value}'
        return f'{client_help}\n'
