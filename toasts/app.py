
"""
toasts.app
~~~~~~~~~~

Main App class.
"""

import sys
import time
import traceback

# TODO: get list of common errors produced by requests
import requests

from .clients import CLIENTS
from .exceptions import AuthError, UnexpectedResponse
from .wrappers import Notifier, Preferences, ErrorNotification


class ToastsApp:
    """
    The main app class that runs the app.
    Attributes:
        config (wrappers.Preferences): Object for getting saved user preferences.
        clients (list): Names of enabled clients.
        notifier (wrappers.Notifier): Used to show notifications.
    """

    def __init__(self):
        self.config = Preferences()
        self.clients = self.config.get("general.clients")
        self.notifier = Notifier(
            timeout=self.config.get("general.notif_timeout"),
            max_show=self.config.get("general.notif_max_show"),
        )

    # FIXME: refactor run method (McCabe rating is 13)
    def run(self):
        """Launch the app and start showing notifications."""
        if not self.clients:
            msg = (
                "No clients enabled - please enable atleast one client "
                "in the config file and restart the app."
            )
            self.notifier.show_error(ErrorNotification(msg=msg))
            # TODO: include location of config file in error message
            self.exit_with_error("No clients enabled")

        client_list = []
        for client in self.clients:
            try:
                client_obj = CLIENTS[client]
                client_list.append(client_obj(config=self.config))
            except KeyError:
                msg = (
                    "Invalid client name specified in config file - {}. "
                    "Please give a valid client name and restart the app."
                ).format(client)
                self.notifier.show_error(ErrorNotification(msg=msg))
                self.exit_with_error('Invalid client name "{}"'.format(client))
            except AuthError as err:
                self.notifier.show_error(ErrorNotification(msg=str(err)))
                self.exit_with_error(msg=str(err))

        while True:
            try:
                for client in client_list:
                    try:
                        notifs = client.get_notifications()
                        self.notifier.show_notif(notifs)
                    except AuthError as err:
                        self.notifier.show_error(ErrorNotification(msg=str(err)))
                        self.exit_with_error(msg=str(err))
                    except UnexpectedResponse as err:
                        sys.stderr.write(str(err) + "\n")
                    except (requests.Timeout, requests.ConnectionError):
                        pass
            except Exception as err:
                msg = (
                    "A critical error caused Toasts to crash. "
                    "Please restart the app."
                )
                self.notifier.show_error(ErrorNotification(msg))
                self.exit_with_error(traceback.format_exc())

            sleep_min = self.config.get("general.check_every")
            time.sleep(sleep_min * 60)  # convert to seconds

    @staticmethod
    def exit_with_error(msg):
        """
        Exit from the app with an exit status of 1.
        Args:
            msg (str): Message to print to stderr.
        """
        sys.exit("ERROR(toasts) - " + msg)
