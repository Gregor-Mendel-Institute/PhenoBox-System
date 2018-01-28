class RemoteError(Exception):
    def __init__(self, message, *args):
        super(RemoteError, self).__init__(message, *args)


class UnavailableError(RemoteError):
    def __init__(self, service_name, *args):
        message = "The requested service({}) is currently unavailable".format(service_name)
        super(UnavailableError, self).__init__(message, *args)


class PostprocessingStackAlreadyExistsError(RemoteError):
    def __init__(self, message, stack_name, stack_id, *args):
        super(PostprocessingStackAlreadyExistsError, self).__init__(message, *args)
        self.name = stack_name
        self.id = stack_id


class PipelineAlreadyExistsError(RemoteError):
    def __init__(self, message, pipeline_name, *args):
        super(PipelineAlreadyExistsError, self).__init__(message, *args)
        self.name = pipeline_name


class InvalidPipelineError(RemoteError):
    def __init__(self, message, *args):
        super(InvalidPipelineError, self).__init__(message, *args)


class InternalError(RemoteError):
    def __init__(self, message, *args):
        super(InternalError, self).__init__(message, *args)


class NotFoundError(RemoteError):
    def __init__(self, message, resource, *args):
        super(NotFoundError, self).__init__(message, *args)
        self.resource = resource
