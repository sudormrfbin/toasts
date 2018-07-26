
"""
toasts.wrappers.py
~~~~~~~~~~~~~~~~~~

Wrapper classes for the app.
"""

import configobj


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
