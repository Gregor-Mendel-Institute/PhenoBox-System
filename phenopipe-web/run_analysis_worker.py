import sys

from server.modules.processing.analysis.analysis_jobs.worker import run

if __name__ == '__main__':
    run('server/config/', sys.argv[1])
