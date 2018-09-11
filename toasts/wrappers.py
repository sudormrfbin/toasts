
"""
toasts.wrappers
~~~~~~~~~~~~~~~

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


class Notification:
    """
    Notification object with metadata about a notification.
    Attributes:
        title (str): Title of the notification.
        client (str): Name of client from which the notification originated.
        uid (int): Unique id of the notification, as provided by the client.
        msg (str): Content of the notification.
    """
    def __init__(self, msg, client, uid, title=None):
        self.msg = msg
        self.client = client
        self.uid = uid
        if title is None:
            self.title = "Notification from {}".format(self.client.title())
        else:
            self.title = title

    def __eq__(self, other):
        return self.uid == other.uid and self.client == other.client


class Notifier:
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
                app_name="toasts",
                timeout=self.disp_timeout,
            )

        msgs_to_show = msgs[0 : self.max_show]
        unshown = len(msgs) - len(msgs_to_show)  # count of suppressed msgs

        for msg in msgs_to_show:
            notify(msg)
            time.sleep(3)  # give some time to read the notification

        if unshown:
            msg = (
                "You have {} more notification(s) from this website. "
                "Please go to the website to see them.".format(unshown)
            )
            notify(msg)

    def show_error(self, msg, title="An error occured in Toasts"):
        """Show an error message as notification. `msg` is a string."""
        self.show_notif(title=title, msgs=[msg], icon="error")


class Session(requests.Session):
    def __init__(self, request_timeout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get = functools.partial(self.get, timeout=request_timeout)

    # TODO: wrap requests.exceptions.ConnectionError and requests.exceptions.Timeout


class _ConfuseConfig(confuse.Configuration):
    """
    A custom Configuration object to be used by `Preferences`. This is *not*
    the object used for fetching preferences by the app.
    """

    def __init__(self, appname, config, default):
        self.config = config  # absolute path to user config
        self.default_config = default  # absolute path to default config file
        super().__init__(appname)

    def user_config_path(self):
        return self.config

    def _add_default_source(self):
        filename = self.default_config
        self.add(confuse.ConfigSource(confuse.load_yaml(filename), filename, True))


class Preferences:
    """
    Class used for fetching preferences.
    """

    CONFIG_DIR = os.path.join(confuse.config_dirs()[0], "toasts")
    USER_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
    DEFAULT_CONFIG_FILE = util.get_default_config_path()

    def __init__(self):
        if not os.path.exists(self.USER_CONFIG_FILE):
            self.create_config_file()
        # confuse looks in system specific directories for config files (config.yaml)
        # by using the app's name
        self._config = _ConfuseConfig(
            appname="toasts",
            config=self.USER_CONFIG_FILE,
            default=self.DEFAULT_CONFIG_FILE,
        )

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
        for key in opt.split("."):
            val = val[key]
        return val.get()
