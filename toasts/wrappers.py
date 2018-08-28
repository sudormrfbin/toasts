
"""
toasts.wrappers.py
~~~~~~~~~~~~~~~~~~

Wrapper objects for the app.
"""

import time
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
            to show. If value is 0, all messages will be shown.
    """
    def __init__(self, timeout, max_show):
        self.disp_timeout = timeout
        self.max_show = max_show

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

        for msg in msgs[0 :self.max_show]:
            notify(msg)
            time.sleep(3)   # give some time to read the notification

        if len(msgs) > self.max_show:
            more = len(msgs) - self.max_show
            msg = (
                'You have {} more notification(s) from this website. '
                'Please go to the website to see them.'
                '\n\nEdit the "max_show" option in the config file to show '
                'more messages in the desktop.'.format(more)
                )
            notify(msg)

    def show_error(self, msg, title='An error occured in Toasts'):
        """Show an error message as notification. `msg` is a string."""
        self.show_notif(title=title, msgs=[msg], icon='error')


class Session(requests.Session):
    def __init__(self, request_timeout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get = functools.partial(self.get, timeout=request_timeout)


class Preferences:
    """
    Class used for fetching preferences.
    """
    def __init__(self):
        # confuse looks in system specific directories for config files (config.yaml)
        self._config = confuse.Configuration(appname='toasts')

    def get_pref(self, opt):
        """
        Return the value of the `opt` option.
        Args:
            opt (str): name of option - "general.clients", "sites.github.token", etc.
        """
        val = self._config
        for key in opt.split('.'):
            val = val[key]
        return val.get()
