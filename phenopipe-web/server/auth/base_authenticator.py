class BaseAuthenticator(object):
    def authenticate(self, username=None, password=None):
        """
        Authenticates the user with the given credentials and returns a dictionary containing the user information

        :param username:
        :param password:

        :return: A dictionary containing at least the following keys: 'username','name','surname','email','groups' or
            None if authentication was not successful
        """
        raise NotImplementedError()
