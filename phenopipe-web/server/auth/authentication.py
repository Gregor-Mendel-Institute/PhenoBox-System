from server.auth.base_authenticator import BaseAuthenticator

_authenticators = []


def register_authenticator(authenticator):
    """
    Registers the given authenticator to be used to authenticate requests.
    The order of registration determines the order in which the system tries to authenticate a user

    :param authenticator: The authenticator to be registered. Has to be a descendant of :class:`.BaseAuthenticator`

    :raise TypeError: if the given authenticator is no descendant of :class:`.BaseAuthenticator`

    :return: None
    """
    if isinstance(authenticator, BaseAuthenticator):
        _authenticators.append(authenticator)
    else:
        raise TypeError("Authenticator must be descendant of server.auth.base_authenticator.BaseAuthenticator")


def is_admin(identity):
    return False


def authenticate(username, password):
    """
    Tries to authenticate the user against all given Authenticators until a match is found or no other Authenticator is available

    :param username:
    :param password:

    :return: A dict containing the user info if successful. None otherwise
    """
    for authenticator in _authenticators:
        user_info = authenticator.authenticate(username, password)
        if user_info is not None:
            return user_info
    return None
