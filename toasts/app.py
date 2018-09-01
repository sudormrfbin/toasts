
"""
toasts.app.py
~~~~~~~~~~~~~~

Main App class.
"""

import sys
import time
import traceback

# TODO: get list of common errors produced by requests
import requests

from . import wrappers
from .clients import CLIENTS
from .exceptions import AuthError, UnexpectedResponse


class ToastsApp():
    """
    The main app class that runs the app.
    Attributed:
        config (wrappers.Preferences): Object for getting saved user preferences.
    """
    def __init__(self):
        """
        Args:
            config_path (str): Path to the user config file for preferences
        """
        self.config = wrappers.Preferences()
        self.clients = self.config.get('general.clients')
        self.notifier = wrappers.Notifier(
            timeout=self.config.get('general.notif_timeout'),
            max_show=self.config.get('general.notif_max_show')
        )

    # FIXME: refactor run method (McCabe rating is 13)
    def run(self):
        """Launch the app and start showing notifications."""
        if not self.clients:
            self.notifier.show_error(
                'No clients enabled - please enable atleast one client in the'
                ' config file and restart the app.'
            )
            # TODO: include location of config file in error message
            self.exit_with_error('No clients enabled')

        client_list = []
        for client in self.clients:
            try:
                client_obj = CLIENTS[client]
                client_list.append(client_obj(config=self.config))
            except KeyError:
                self.notifier.show_error(
                    "Invalid client name specified in config file - {}.\
                     Please give a valid client name and restart the app.\
                    ".format(client)
                )
                self.exit_with_error('Invalid client name "{}"'.format(client))
            except AuthError as err:
                msg = 'Invalid credentials for {}.'.format(client_obj.NAME)
                self.notifier.show_error(title=str(err), msg=msg)
                self.exit_with_error(msg)

        while True:
            try:
                for client in client_list:
                    try:
                        notifs = client.get_notifications()
                        self.notifier.show_notif(
                            title='Notification from {}'.format(client.NAME.title()),
                            msgs=notifs,
                            icon=client.NAME
                        )
                    except AuthError as err:
                        msg = 'Invalid credentials for {}.'.format(client.NAME)
                        self.notifier.show_error(title=str(err), msg=msg)
                        self.exit_with_error(msg)
                    except UnexpectedResponse as err:
                        sys.stderr.write(str(err) + '\n')
                    except (requests.Timeout, requests.ConnectionError):
                        pass
            except Exception as err:
                self.notifier.show_error(
                    'A critical error caused Toasts to crash.\
                     Please restart the app.'
                )
                self.exit_with_error(traceback.format_exc())

            sleep_sec = self.config.get('general.check_every')
            time.sleep(sleep_sec * 60)   # convert to seconds

    @staticmethod
    def exit_with_error(msg):
        """
        Exit from the app with an exit status of 1.
        Args:
            msg (str): Message to print to stderr.
        """
        sys.exit('ERROR(toasts) - ' + msg)
