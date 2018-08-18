
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


def show_notif(title, msg, icon):
    """Show a notification with `title` and description `msg`"""
    icon_path = util.get_icon(icon)
    plyer.notification.notify(
        title=title,
        message=msg,
        app_icon=icon_path,
        app_name='toasts',
        timeout=7
    )

def show_error(msg, title='An error occured in Toasts'):
    """Show an error message as notification"""
    show_notif(title=title, msg=msg, icon='error')


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
