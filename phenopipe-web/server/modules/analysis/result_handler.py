import logging
import threading
import time

from rq.job import Job
from rq.registry import FinishedJobRegistry

from server.extensions import db, redis_db
from server.models import TimestampModel
from server.models.analysis_model import AnalysisModel
from server.modules.analysis.analysis_jobs.job_type import JobType


class ResultHandler(threading.Thread):
    def __init__(self):
        super(ResultHandler, self).__init__()
        self._stop = threading.Event()
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        print 'starting result worker'
        self._logger.info('Starting Result Worker')
        registry = FinishedJobRegistry('analysis', connection=redis_db)
        while not self.stopped():
            if registry.count == 0:
                time.sleep(3)
                continue

            job_ids = registry.get_job_ids()
            for job_id in job_ids:
                print(job_id)
                job = Job.fetch(job_id, connection=redis_db)
                # registry.remove(job)
                # continue
                result = job.result
                print(result)
                if result['type'] == JobType.iap_import:
                    pass
                    # self.handle_import_result(job.result)
                elif result['type'] == JobType.iap_analysis:
                    pass
                    #self.handle_analysis_result(job.result)
                elif result['type'] == JobType.iap_export:
                    pass
                    #self.handle_export_result(job.result)
                registry.remove(job)

    def handle_import_result(self, result):
        from server.app import server_app
        with server_app.app_context():
            timestamp = db.session.query(TimestampModel).get(result['timestamp_id'])
            timestamp.iap_exp_id = result['response']['experiment_id']
            db.session.commit()

    def handle_analysis_result(self, result):
        from server.app import server_app
        with server_app.app_context():
            analysis = db.session.query(AnalysisModel).filter(
                AnalysisModel.timestamp_id == result['timestamp_id']).one()
            analysis.iap_id = result['response']['result_id']
            analysis.started_at = result['response']['started_at']
            analysis.finished_at = result['response']['finished_at']
            db.session.commit()

    def handle_export_result(self, result):
        from server.app import server_app
        with server_app.app_context():
            analysis = db.session.query(AnalysisModel).filter(
                AnalysisModel.timestamp_id == result['timestamp_id']).one()
            analysis.export_path = result['response']['path']
            db.session.commit()
