from server.modules.printer.print_job import PrintJob
from server.utils import RedisQueue, Empty


class PrintQueue(RedisQueue):
    namespace = 'printer'

    def __init__(self, connection):
        super(PrintQueue, self).__init__(connection, 'job_bundles', self.namespace)
        self._connection = connection
        self._current_bundle_id = None
        self._current_job_queue = None

    def enqueue(self, bundle):
        # Handle status keys too
        super(PrintQueue, self).enqueue(bundle.id)
        job_queue = RedisQueue(self._connection, bundle.id, self.namespace)
        for job in bundle.jobs:
            job_queue.enqueue(job.serialize())

    def dequeue_job(self, block, timeout):
        if self._current_bundle_id is None:
            bundle_id = super(PrintQueue, self).dequeue()
            self._current_bundle_id = bundle_id
            self._current_job_queue = RedisQueue(self._connection, bundle_id, self.namespace)
        try:
            return PrintJob.load(self._current_job_queue.dequeue(block, timeout))
        except Empty:
            self._current_bundle_id = None
            self._current_job_queue = None
            return self.dequeue_job(block, timeout)

    def requeue_job(self, job):
        self._current_job_queue.requeue(job)
