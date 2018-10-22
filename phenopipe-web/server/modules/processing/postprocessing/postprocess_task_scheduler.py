from threading import RLock

from graphql_relay import to_global_id

from server.extensions import db
from server.models import PostprocessModel, SnapshotModel
from server.modules.processing.analysis.analysis import get_iap_pipeline
from server.modules.processing.exceptions import AlreadyFinishedError
from server.modules.processing.postprocessing.postprocessing_jobs import invoke_r_postprocess
from server.modules.processing.postprocessing.postprocessing_task import PostprocessingTask


class PostprocessTaskScheduler:
    _lock = RLock()
    _timeout = 43200  # 12h

    def __init__(self, connection, namespace, rq_queue, log_store):
        """
        Initializes the Task Scheduler with a redis connection and the according namespace which it will use for its keys
        inside Redis.
        :param connection: The redis connection which is used by the Scheduler
        :param namespace: The top level key which will be used inside redis
        """
        self._connection = connection
        self._namespace = namespace
        self._rq_queue = rq_queue
        self._log_store = log_store

    @property
    def log_store(self):
        return self._log_store

    def _get_tracking_set_key(self, username):
        return '{}:{}'.format(self._namespace, username)

    def _get_task_hash_key(self, analysis_id):
        return '{}:{}'.format(self._namespace, str(analysis_id))

    def fetch_all_task_keys(self, username):
        return self._connection.smembers(self._get_tracking_set_key(username))

    def fetch_all_tasks(self, username):
        tasks = []
        keys = self.fetch_all_task_keys(username)
        for key in keys:
            tasks.append(PostprocessingTask.from_key(self._connection, key))
        return tasks

    def submit_task(self, analysis, snapshots, control_group, stack, note, username, experiment,
                    depends_on=None):
        """
       Creates a Background Job for running a specific postprocessing stack on an analysis result and enqueues it.

       The Job will only be enqueued if there is no corresponding entry in the 'postprocess' table

       :param analysis: The :class:`~server.models.analysis_model.AnalysisModel` instance to be postprocessed
       :param stack: The instance of the Postprocessing stack that should be used
       :param note: A note from the user to make it easier to identify a postprocess
       :param username: The username of the experiment owner
       :param experiment: The :class:`~server.models.experiment_model.ExperimentModel` to which the data belongs
       :param depends_on: A job which must be finished before the postprocessing can be started

       :return: A Tuple containing the created :class:`~server.modules.postprocessing.postprocessing_task.PostprocessingTask` and the :class:`~server.models.analysis_model.PostprocessModel` instance
       """
        postprocess, created = PostprocessModel.get_or_create(analysis.id, stack.id, control_group.id, snapshots, note)
        if created:
            db.session.commit()

            task_name = 'Postprocess IAP analysis'
            pipeline = get_iap_pipeline(username, analysis.pipeline_id)
            # TODO think about a way to link to the according analysis page on the frontend
            task_description = 'Apply postprocessing stack "{}" to results of analysis for experiment "{}" at timestamp({}) with pipeline "{}".'.format(
                stack.name, experiment.name,
                analysis.timestamp.created_at.strftime("%a %b %d %H:%M:%S UTC %Y"), pipeline.name)
            task = PostprocessingTask(self._connection, analysis.id, stack.id, self._rq_queue.name, task_name,
                                      task_description)
            task.update_message("Postprocessing Task Enqueued")
            task.save()
            self._connection.sadd(self._get_tracking_set_key(username), task.key)

            all_snapshots = db.session.query(SnapshotModel) \
                .filter(SnapshotModel.timestamp_id == analysis.timestamp.id) \
                .all()
            # TODO embed building of difference into query
            snap_set = set(snapshots)
            excluded_snapshots = [snap for snap in all_snapshots if snap not in snap_set]
            excluded_plants = [snapshot.plant.full_name for snapshot in excluded_snapshots]

            description = 'Run postprocessing stack({}) on the results of analysis ({})'.format(
                stack.name,
                to_global_id('Analysis', analysis.id))

            job = self._rq_queue.enqueue_call(invoke_r_postprocess,
                                              (experiment.name, postprocess.id, analysis.id, excluded_plants,
                                               analysis.export_path,
                                               stack.id, stack.name, username, task.key),
                                              result_ttl=-1,
                                              ttl=-1,
                                              description=description,
                                              meta={'name': 'postprocessing_job'},
                                              depends_on=depends_on
                                              )
            task.processing_job = job
            task.save()
            return task, postprocess

        else:
            if postprocess.finished_at is None:
                return PostprocessingTask.from_key(self._connection,
                                                   PostprocessingTask.key_for(analysis.id, stack.id)), postprocess
            else:
                raise AlreadyFinishedError('Postprocess', postprocess.id,
                                           'The requested postprocessing stack has already been processed')
