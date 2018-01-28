from uuid import uuid4


class PrintJobBundle:
    def __init__(self, identifier):
        self._identifier = identifier
        self._id = uuid4()
        self._print_jobs = []

    def add_job(self, print_job):
        self._print_jobs.append(print_job)

    @property
    def id(self):
        return self._id

    @property
    def jobs(self):
        return self._print_jobs
