class DataError(Exception):
    def __init__(self, message, *args):
        super(DataError, self).__init__(message, *args)


class ConstraintViolationError(DataError):
    def __init__(self, message, *args):
        super(ConstraintViolationError, self).__init__(message, *args)


class ConflictingDataError(DataError):
    def __init__(self, message, *args):
        super(ConflictingDataError, self).__init__(message, *args)


class InvalidMutationRequestError(DataError):
    def __init__(self, message, *args):
        super(InvalidMutationRequestError, self).__init__(message, *args)


class UnableToDeleteError(DataError):
    def __init__(self, message, *args):
        super(UnableToDeleteError, self).__init__(message, *args)


class UnknownDataError(DataError):
    def __init__(self, message, *args):
        super(UnknownDataError, self).__init__(message, *args)
