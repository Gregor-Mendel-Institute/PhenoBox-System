from threading import RLock

from flask import current_app

from server.extensions import db
from server.models import AnalysisModel
from server.modules.processing.analysis import invoke_iap_import, invoke_iap_analysis, invoke_iap_export
from server.modules.processing.analysis.analysis_jobs.iap_analysis_jobs import dummy_job
from server.modules.processing.analysis.analysis_task import AnalysisTask
from server.modules.processing.exceptions import AlreadyFinishedError


class AnalysisTaskScheduler(object):
    _lock = RLock()
    _timeout_import = 43200  # 12h
    _timeout_analysis = 86400  # 24h
    _timeout_export = 600  # 10min

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

    def _get_import_job_id_key(self, timestamp_id):
        return '{}:{}:import_job'.format(self._namespace, str(timestamp_id))

    def _get_tracking_set_key(self, username):
        return 'ana_tasks:{}'.format(username)

    def _get_task_hash_key(self, timestamp_id, pipeline_id):
        return '{}:{}:{}'.format(self._namespace, str(timestamp_id), str(pipeline_id))

    def _get_import_job_id(self, timestamp_id):
        return self._connection.get(self._get_import_job_id_key(timestamp_id))

    def fetch_all_task_keys(self, username):
        return self._connection.smembers(self._get_tracking_set_key(username))

    def fetch_all_tasks(self, username):
        tasks = []
        keys = self.fetch_all_task_keys(username)
        for key in keys:
            tasks.append(AnalysisTask.from_key(self._connection, key))
        return tasks

    def submit_dummies(self, timestamp_id, pipeline_id, username):
        task_name = 'Dummy Task'
        task_description = 'Dummy Task for testing'
        task = AnalysisTask(self._connection, timestamp_id, pipeline_id, self._rq_queue.name, task_name,
                            task_description)
        task.message = "Analysis Task enqueued"
        task.save()
        self._connection.sadd(self._get_tracking_set_key(username), task.key)

        import_job = self._rq_queue.enqueue_call(dummy_job, ('import dummy', task.key),
                                                 result_ttl=-1,
                                                 ttl=-1,
                                                 timeout=self._timeout_import,
                                                 description='Dummy for import task'
                                                 )
        task.import_job = import_job
        analysis_job = self._rq_queue.enqueue_call(dummy_job, ('analysis dummy', task.key),
                                                   result_ttl=-1,
                                                   ttl=-1,
                                                   timeout=self._timeout_import,
                                                   description='Dummy for analysis task',
                                                   depends_on=import_job
                                                   )
        task.analysis_job = analysis_job
        export_job = self._rq_queue.enqueue_call(dummy_job, ('export dummy', task.key),
                                                 result_ttl=-1,
                                                 ttl=-1,
                                                 timeout=self._timeout_import,
                                                 description='Dummy for export task',
                                                 depends_on=analysis_job
                                                 )
        task.export_job = export_job
        task.save()
        return task, None

    def submit_task(self, timestamp, experiment_name, coordinator, scientist, input_path, output_path,
                    pipeline, username, local_path):
        """
        Creates and Enqueues the necessary background jobs to import, analyze and export the data of the given timestamp

        :param timestamp: The timestamp to be analyzed
        :param experiment_name: The name of the experiment the timestamp belongs to
        :param coordinator: The name of the experiment coordinator
        :param scientist: The name of the scientist conducting this experiment
        :param input_path: The path, as SMB URL, where the input data (images) are stored
        :param output_path: The path, as SMB URL, where the exported data should be stored
        :param pipeline: Instance of an IAP Pipeline object which should be used for analysis
        :param username: The username of the User requesting this process
        :param local_path: The path to the data on the local system
        """
        analysis, created = AnalysisModel.get_or_create(timestamp.id, pipeline.id)
        if created:
            db.session.commit()

            task_name = 'Analyse timestamp data with IAP'
            task_description = 'Full IAP Analysis for experiment "{}" at timestamp(Date:{}) with pipeline "{}".'.format(
                experiment_name,
                timestamp.created_at.strftime("%a %b %d %H:%M:%S UTC %Y"), pipeline.name)
            task = AnalysisTask(self._connection, timestamp.id, pipeline.id, self._rq_queue.name, task_name,
                                task_description)
            task.message = "Analysis Task enqueued"
            task.save()
            self._connection.sadd(self._get_tracking_set_key(username), task.key)
            # Lock to ensure only one import job is executed for multiple pipelines
            self._lock.acquire()
            import_job = None
            if timestamp.iap_exp_id is None:
                import_job_id = self._get_import_job_id(timestamp.id)
                if import_job_id is None:
                    description = 'Import Image data of experiment "{}" at timestamp [{}] to IAP'.format(
                        experiment_name, timestamp.created_at.strftime("%a %b %d %H:%M:%S UTC %Y"))
                    import_job = self._rq_queue.enqueue_call(invoke_iap_import, (timestamp.id, experiment_name,
                                                                                 coordinator,
                                                                                 scientist,
                                                                                 local_path, input_path, username,
                                                                                 task.key),
                                                             result_ttl=-1,
                                                             ttl=-1,
                                                             timeout=self._timeout_import,
                                                             description=description,
                                                             meta={'name': 'import_job'}
                                                             )

                    self._connection.set(self._get_import_job_id_key(timestamp.id), str(import_job.id))
                else:
                    import_job = self._rq_queue.fetch_job(import_job_id)
            task.import_job = import_job
            self._lock.release()
            description = 'Analyse the data of timestamp [{}] with the pipeline "{}" in IAP'.format(
                timestamp.created_at.strftime("%a %b %d %H:%M:%S UTC %Y"), pipeline.name)
            analysis_job = self._rq_queue.enqueue_call(invoke_iap_analysis, (analysis.id, timestamp.id,
                                                                             username, task.key,
                                                                             timestamp.iap_exp_id),
                                                       result_ttl=-1,
                                                       ttl=-1,
                                                       timeout=self._timeout_analysis,
                                                       description=description,
                                                       meta={'name': 'analysis_job'},
                                                       depends_on=import_job)

            task.analysis_job = analysis_job
            shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
            description = 'Export the IAP results for timestamp [{}] for further use'.format(
                timestamp.created_at.strftime("%a %b %d %H:%M:%S UTC %Y"))
            export_job = self._rq_queue.enqueue_call(invoke_iap_export,
                                                     (timestamp.id, output_path, username,
                                                      shared_folder_map, task.key),
                                                     result_ttl=-1,
                                                     ttl=-1,
                                                     timeout=self._timeout_export,
                                                     description=description,
                                                     meta={'name': 'export_job'},
                                                     depends_on=analysis_job)

            task.export_job = export_job
            task.save()
            return task, analysis
        else:
            if analysis.finished_at is None:
                return AnalysisTask.from_key(self._connection,
                                             AnalysisTask.key_for(analysis.timestamp_id,
                                                                  analysis.pipeline_id)), analysis
            else:
                raise AlreadyFinishedError(AnalysisModel, analysis.id,
                                           'The requested analysis has already been processed')
