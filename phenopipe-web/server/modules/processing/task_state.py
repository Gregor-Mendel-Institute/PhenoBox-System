from enum import Enum


class TaskState(Enum):
    CREATED = 1
    QUEUED = 2
    RUNNING = 3
    FINISHED = 4
    FAILED = 5

    def __str__(self):
        return self.name

    @property
    def state(self):
        return self.value
