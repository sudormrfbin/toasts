
"""
toasts.clients.github
~~~~~~~~~~~~~~~~~~~~~

Client for getting notifications from GitHub - https://www.github.com

See https://developer.github.com/v3/activity/notifications/ for api docs.
"""


from .base import PersonalAccessTokenClient
from ..wrappers import ClientNotification
from ..exceptions import AuthError, UnexpectedResponse


class GitHubClient(PersonalAccessTokenClient):

    NAME = "github"
    API_ENDPOINT = "https://api.github.com/notifications"

    def get_notifications(self):
        response = self.session.get(self.API_ENDPOINT)

        if response.status_code == 200:
            notifs = self._parse_json_data(response.json())
            return [ClientNotification(**data) for data in notifs]

        elif response.status_code == 304:  # not modified; no new notifications
            return []
        elif response.status_code == 401:  # unauthorized
            raise AuthError("GitHub")
        else:
            raise UnexpectedResponse("GitHub", response.status_code)

    def _parse_json_data(self, data):
        # See the response section in
        # https://developer.github.com/v3/activity/notifications#list-your-notifications

        notifs = []

        for event in data:
            metainfo = event["subject"]
            metainfo["repo_name"] = event["repository"]["full_name"]
            msg = "{type}: {title} ({repo_name})".format(**metainfo)

            parsed = {"msg": msg, "uid": event["id"], "client": "github"}
            notifs.append(parsed)

        return notifs
