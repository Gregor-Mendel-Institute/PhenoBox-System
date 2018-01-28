from enum import Enum


class Status(Enum):
    created = 1
    pending = 2
    running = 3
    finished = 4
    error = 5

    def __str__(self):
        return self.name

    @property
    def status(self):
        return self.value
