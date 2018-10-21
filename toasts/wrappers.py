
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


class BaseNotification:
    """
    Base class for Notification objects, holding metadata about a notification.
    Attributes:
        title (str): Title of the notification.
        msg (str): Content of the notification.
        icon_path (str): Path to the icon that should be used when displaying.
    """

    def __init__(self, title, msg, icon):
        # NOTE: `icon` is the name of the icon to be used, without the extension
        # like github, and not github.png; it will be expanded to the absolute path
        self.title = title
        self.msg = msg
        self.icon_path = util.get_icon(icon)


class ClientNotification(BaseNotification):
    """
    Notification object to be used when there is a notification from a client.
    Attributes:
        client (str): Name of client from which the notification originated.
        uid (int): Unique id of the notification, as provided by the client.
    """

    def __init__(self, msg, client, uid, title=None):
        self.client = client
        self.uid = uid
        if title is None:
            title = "Notification from {}".format(client.title())
        super().__init__(title=title, msg=msg, icon=client)

    def __eq__(self, other):
        return self.uid == other.uid and self.client == other.client


class ErrorNotification(BaseNotification):
    """
    Notification object used for showing errors.
    """

    def __init__(self, msg, title="An error occured in Toasts"):
        super().__init__(title=title, msg=msg, icon="error")


class Notifier:
    """
    Show desktop notifications.
    Attributes:
        disp_timeout (int): Show a notification for this much seconds.
        max_show (int):
            Maximum number of notifications to show at a time.
            Show only this much number of notifications, if there are
            too many to show (more than `max_show` in `msgs` argument of
            `show_notif` method). An additional notification will be shown,
            saying that there are `len(msgs) - max_show` more notifications
            to show. If value is -1, all messages will be shown.
        _history (list of ClientNotification):
            Previously shown notifications (in this instance of the app).
    """

    def __init__(self, timeout, max_show):
        self.disp_timeout = timeout
        self.max_show = max_show if max_show >= 0 else None
        self._history = []

    def show_notif(self, notifs):
        """
        Show a notification.
        Args:
            notifs (list of ClientNotification):
                List of notifications to show. All the notifications will
                be from the same client at a time.
        """

        new_notifs = [n for n in notifs if n not in self._history]
        self._history.extend(new_notifs)
        msgs_to_show = new_notifs[0 : self.max_show]
        unshown = len(new_notifs) - len(msgs_to_show)  # count of suppressed msgs

        for notification in msgs_to_show:
            self._notify(notification)
            time.sleep(3)  # give some time to read the notification

        if unshown:
            msg = (
                "You have {} more notification(s) from this website. "
                "Please go to the website to see them.".format(unshown)
            )
            # get name of client that made the notifs; all are from the same client
            client = notifs[0].client
            n = ClientNotification(msg=msg, client=client, uid=None)
            self._notify(n)

    def show_error(self, error):
        """
        Show an error message as notification.
        Args:
            error (ErrorNotification): Notification object.
        """
        self._notify(error)

    def _notify(self, notif_obj):
        """
        Actual method that shows a notification.
        Args:
            notif_obj (BaseNotification): Notification object.
        """
        plyer.notification.notify(
            title=notif_obj.title,
            message=notif_obj.msg,
            app_icon=notif_obj.icon_path,
            app_name="toasts",
            timeout=self.disp_timeout,
        )


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
            opt (str):
                name of option - "general.clients", "sites.github.token", etc.
        """
        val = self._config
        for key in opt.split("."):
            val = val[key]
        return val.get()
