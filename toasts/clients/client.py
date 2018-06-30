
"""
toasts.clients.client
~~~~~~~~~~~~~~~~~~~~~

This module contains ABCs for designing concrete client classes
"""

from abc import ABCMeta, abstractmethod

import requests

class Client(metaclass=ABCMeta):
    """
    Base class for all clients.

    Attributes:
        NAME (str): Name of the client, like 'github', 'stack overflow'.
        API_ENDPOINT (str): URL of the api endpoint used to get notifications.
        session (requests.Session): Session object to do api requests with.
    """

    NAME = None
    API_ENDPOINT = None

    def __init__(self, config):
        """
        Args:
            config (configobj.ConfigObj): Contains preferences set by user.
        """
        self.config = config
        self.session = requests.Session()

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def get_notifications(self):
        """
        Get notifications from the specified site through `API_ENDPOINT`.

        Returns:
            list of str: Text to displayed as notification. Each item in
                the list is a seperate notification. Empty list is returned if
                there are no new notifications.
        Raises:
            toasts.exceptions.AuthError: Invalid credentials.
        """
        pass

    @abstractmethod
    def _parse_json_data(self, data):
        """
        Parse the json data containing the notifications. Called by
        `get_notifications`.

        Args:
            data(json): Python object from `json.loads`.

        Returns:
            list of str: Each item of the list is a notification to be
                displayed as such.
        """
        pass
