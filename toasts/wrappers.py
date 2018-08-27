
"""
toasts.wrappers.py
~~~~~~~~~~~~~~~~~~

Wrapper objects for the app.
"""

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
    """
    def __init__(self, timeout):
        self.disp_timeout = timeout

    def show_notif(self, title, msg, icon):
        """
        Show a notification.
        Args:
            title (str): Title of notification.
            msg (str): Content of the notification.
            icon (str): Name of icon to be used.
                `icon` should be the name of a file in `toasts/data/icons/`,
                stripped off it's extension. Eg: github (not github.png)
        """
        icon_path = util.get_icon(icon)
        plyer.notification.notify(
            title=title,
            message=msg,
            app_icon=icon_path,
            app_name='toasts',
            timeout=self.disp_timeout
        )

    def show_error(self, msg, title='An error occured in Toasts'):
        """Show an error message as notification"""
        self.show_notif(title=title, msg=msg, icon='error')


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
