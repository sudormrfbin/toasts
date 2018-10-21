
"""
toasts.exceptions
~~~~~~~~~~~~~~~~~

Contains exceptions raised by toasts.
"""


class ToastError(Exception):
    """Base class for all toasts exceptions."""

    pass


class AuthError(ToastError):
    """Raised when invalid credentials are supplied."""

    def __init__(self, client):
        msg = "Invalid credentials for authentication in {}".format(client)
        super().__init__(msg)


class UnexpectedResponse(ToastError):
    """Raised when the status code of an operation is not the expected one."""

    def __init__(self, client, status_code):
        msg = "Unexpected response from {0} (status code: {1})".format(
            client, status_code
        )
        super().__init__(msg)
