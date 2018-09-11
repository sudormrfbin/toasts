
"""
toasts.util
~~~~~~~~~~~

Utilities for toasts.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))


def get_icon(icon):
    """Get absolute path to `icon`, where icon is a string, like 'github'."""
    icon += ".png"  # TODO: see if png is supported across all platforms
    return os.path.join(HERE, "data", "icons", icon)


def get_default_config_path():
    """Get the path to the default config file (data/config.yaml)."""
    return os.path.join(HERE, "data", "config.yaml")
