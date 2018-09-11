
"""
toasts.clients
~~~~~~~~~~~~~~

Contains client classes used for fetching notifications from various websites.
"""

from .github import GitHubClient

CLIENTS = {"github": GitHubClient}
