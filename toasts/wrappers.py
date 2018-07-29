
"""
toasts.wrappers.py
~~~~~~~~~~~~~~~~~~

Wrapper objects for the app.
"""

import plyer
import configobj

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


class Preferences:
    """
    Class used for fetching preferences
    """
    def __init__(self, path):
        """
        Args:
            path (str): Path to the config file
        """
        self._config = configobj.ConfigObj(path)

    def get_pref(self, section, item):
        """
        Return the value of the `item` option in the `section` sub-division
        of the user's preferences
        """
        return self._config[section][item]
