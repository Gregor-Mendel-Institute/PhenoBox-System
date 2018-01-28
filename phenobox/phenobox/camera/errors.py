class CameraError(Exception):
    def __init__(self, message, detail=None):
        self.message = message
        if detail:
            self.detail = detail

    def __str__(self):
        return '%s - %s' % (self.message, self.detail)


class CaptureError(CameraError):
    def __init__(self, message, detail=None):
        super(CaptureError, self).__init__(message, detail)

    def __str__(self):
        return '%s - %s' % (self.message, self.detail)

class ConnectionError(CameraError):
    def __init__(self, message, detail=None):
        super(ConnectionError, self).__init__(message, detail)

    def __str__(self):
        return '%s - %s' % (self.message, self.detail)
