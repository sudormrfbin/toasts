
"""
toasts.wrappers.py
~~~~~~~~~~~~~~~~~~

Wrapper objects for the app.
"""

import os
import time
import shutil
import functools

import plyer
import confuse
import requests

from . import util


class Notifier():
    """
    Show desktop notifications.
    Attributes:
        disp_timeout (int): Show a notification for this much seconds.
        max_show (int): Maximum number of notifications to show at a time.
            Show only this much number of notifications, if there are
            too many to show (more than `max_show` in `msgs` argument of
            `show_notif` method). An additional notification will be shown,
            saying that there are `len(msgs) - max_show` more notifications
            to show. If value is -1, all messages will be shown.
    """
    def __init__(self, timeout, max_show):
        self.disp_timeout = timeout
        self.max_show = max_show if max_show >= 0 else None

    def show_notif(self, title, msgs, icon):
        """
        Show a notification.
        Args:
            title (str): Title of notification.
            msgs (iterable of str): List of notifications to display.
                Every item in `msgs` is a message that has to displayed in
                seperate notifications. Every item will be displayed unless
                the `notif_max_show` attribute has a non-zero value. All the
                notifications will have the same icon and title.
            icon (str): Name of icon to be used.
                `icon` should be the name of a file in `toasts/data/icons/`,
                stripped off it's extension. Eg: github (not github.png)
        """
        icon_path = util.get_icon(icon)
        def notify(msg):
            plyer.notification.notify(
                title=title,
                message=msg,
                app_icon=icon_path,
                app_name='toasts',
                timeout=self.disp_timeout
            )

        msgs_to_show = msgs[0 : self.max_show]
        unshown = len(msgs) - len(msgs_to_show)   # count of suppressed msgs

        for msg in msgs_to_show:
            notify(msg)
            time.sleep(3)   # give some time to read the notification

        if unshown:
            msg = (
                'You have {} more notification(s) from this website. '
                'Please go to the website to see them.'.format(unshown)
                )
            notify(msg)

    def show_error(self, msg, title='An error occured in Toasts'):
        """Show an error message as notification. `msg` is a string."""
        self.show_notif(title=title, msgs=[msg], icon='error')


class Session(requests.Session):
    def __init__(self, request_timeout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get = functools.partial(self.get, timeout=request_timeout)

    # TODO: wrap requests.exceptions.ConnectionError and requests.exceptions.Timeout

class Preferences:
    """
    Class used for fetching preferences.
    """
    CONFIG_DIR = os.path.join(confuse.config_dirs()[0], 'toasts')
    USER_CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.yaml')
    DEFAULT_CONFIG_FILE = util.get_default_config_path()

    def __init__(self):
        if not os.path.exists(self.USER_CONFIG_FILE):
            self.create_config_file()
        # confuse looks in system specific directories for config files (config.yaml)
        self._config = confuse.Configuration(appname='toasts')
        # TODO: supply 2nd argument of Configuration

    def create_config_file(self):
        """
        Create a config file with default settings in `CONFIG_DIR`. Overwrites
        existing config file.
        """
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
        shutil.copy(self.DEFAULT_CONFIG_FILE, self.CONFIG_DIR)

    def get(self, opt):
        """
        Return the value of the `opt` option.
        Args:
            opt (str): name of option - "general.clients", "sites.github.token", etc.
        """
        val = self._config
        for key in opt.split('.'):
            val = val[key]
        return val.get()
