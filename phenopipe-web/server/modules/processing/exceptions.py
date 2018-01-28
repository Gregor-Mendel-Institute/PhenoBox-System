class ProcessingError(Exception):
    def __init__(self, message, *args):
        super(ProcessingError, self).__init__(message, *args)


class AlreadyRunningError(ProcessingError):
    def __init__(self, username, status_id, message, *args):
        super(AlreadyRunningError, self).__init__(message, *args)
        self.username = username
        self.status_id = status_id


class AlreadyFinishedError(ProcessingError):
    def __init__(self, schema_name, db_id, message, *args):
        super(AlreadyFinishedError, self).__init__(message, *args)
        self.schema_name = schema_name
        self.db_id = db_id


class InvalidPathError(ProcessingError):
    def __init__(self, path, message, *args):
        super(InvalidPathError, self).__init__(message, *args)
        self.path = path


class AnalysisDataNotPresentError(ProcessingError):
    def __init__(self, analysis_db_id, message, *args):
        super(AnalysisDataNotPresentError, self).__init__(message, *args)
        self.analysis_db_id = analysis_db_id
