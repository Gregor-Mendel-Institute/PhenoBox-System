class ApiError(Exception):
    def __init__(self, message, *args):
        super(ApiError, self).__init__(message, *args)


class ForbiddenActionError(ApiError):
    def __init__(self, message, username, *args):
        super(ForbiddenActionError, self).__init__(message, *args)
        self.username = username

