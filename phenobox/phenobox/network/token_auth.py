import time

import jwt
import requests
from requests import Request

from network import UnableToAuthenticateError


class TokenAuth:
    """
    Class used to implement JWT Token authentication
    """
    _id_token = None
    _refresh_token = None
    _username = None
    _password = None

    # TODO implement logging

    def __init__(self, url, refresh_url, username, password):
        self._url = url
        self._refresh_url = refresh_url
        self._username = username
        self._password = password

    def is_authenticated(self):
        """
        Checks if there is a valid token present

        :return: True if there is a valid token, False otherwise
        """
        if self._id_token is not None:
            remaining_sec = self.get_remaining_time(self._id_token)
            # 5 Seconds are used to not run into problems when it times out shortly after checking
            if remaining_sec > 5:
                return True
        return False

    def check_and_auth(self):
        """
        Checks if there is a valid token present. If so return True.
        If no valid authentication token is available it checks if there is a valid refresh token.
        If so it is used to obtain a new authentication token.
        If not a whole new authentication request is sent to the server to obtain a new authentication and refresh tokens

        :return: True if authentication was successful, False otherwise
        """
        if self.is_authenticated():
            return True
        if self.can_refresh():
            return self.reauth()
        return self.auth()

    def can_refresh(self):
        """
        Checks if the refresh token is not expired already

        :return: True if the refresh token is still usable, False otherwise
        """
        
        # 5 Seconds are used to not run into problems when it times out shortly after checking
        return self.get_remaining_time(self._refresh_token) > 5

    def get_remaining_time(self, token):
        """
        Returns the remaining time in seconds until the given token expires. If the passed token is None the function
        will return a value of -1

        :param token: The token to be checked

        :return: The remaining time in seconds, or -1 if the given token is None
        """
        if token is not None:
            content = jwt.decode(token, verify=False)
            exp = content.get('exp')
            t = time.time()
            return exp - t
        else:
            return -1

    def auth(self):
        """
        Sends an authentication request to the server to obtain a pair of access and refresh token.

        :return: True if the authentication was successful, False otherwise
        """
        payload = {'username': self._username, 'password': self._password}
        r = requests.post(self._url,
                          json=payload)
        if r.status_code != 200:
            return False
        self._id_token = r.json()['access_token']
        self._refresh_token = r.json()['refresh_token']
        if self._id_token is None:
            return False
        return True

    def reauth(self):
        """
        Sends a reauthentication request to the server to obtain a new authorization token

        :return: True if the reauthentication was successful, False otherwise
        """
        r = requests.post(self._refresh_url, headers={'Authorization': 'Bearer ' + self._refresh_token})
        if r.status_code != 200:
            return False
        self._id_token = r.json()['access_token']
        return True

    def prep_post(self, url, data):
        """
        Prepares a POST request which has the the Authorization header set.

        :param url: The endpoint to send the request to
        :param data: The payload to be used

        :raises UnableToAuthenticateError: if no valid authorization token is available and no new toke could be obtained

        :return: The prepared request with payload and authorization header
        """
        if not self.check_and_auth():
            raise UnableToAuthenticateError()
        req = Request('POST', url, data=data)
        prepped = req.prepare()
        prepped.headers['Authorization'] = 'Bearer ' + self._id_token
        return prepped
