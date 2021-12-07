
import logging
from client_settings import ClientSettings
from typing import Optional, Callable
from threading import Thread


class ClientHelpers:
    def __init__(self, logging_object: logging, client_settings: ClientSettings):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging_object.INFO)
        self._client_settings: ClientSettings = client_settings

        self.receive_thread: Optional[Thread] = None

    @staticmethod
    def notification_formatted_message(client_id: str, message: str) -> str:
        notification_formatted_message = f'{client_id}: {message}'
        if len(message) > 58:
            notification_substr = notification_formatted_message[0:57]
            return f'{notification_substr}...'
        else:
            return notification_formatted_message

    def thread_it(self, threaded_function: Callable[[], None]) -> None:
        self.receive_thread = Thread(target=threaded_function)
        self.receive_thread.start()

    def close_notify(self) -> None:
        if self._client_settings.get_current_platform() == 'Linux':
            self._client_settings.linux_notify.uninit()
