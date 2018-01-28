class ServerError(Exception):
    def __init__(self, message, *args):
        super(ServerError, self).__init__(message, *args)


class ServerUnableToSaveImageError(ServerError):
    def __init__(self, message, *args):
        super(ServerUnableToSaveImageError, self).__init__(message, *args)


class UnableToAuthenticateError(Exception):
    def __init__(self, message='Unable to authenticate', *args):
        super(UnableToAuthenticateError, self).__init__(message, *args)
