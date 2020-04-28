"Logging wrapper module"

import inspect
import logging
import os
import psutil
import sys
import uuid

from datetime import datetime
from logging.handlers import WatchedFileHandler
from pythonjsonlogger import jsonlogger

SCITE_ENV = os.environ.get('SCITE_ENV', 'development')
LOGGER_NAME = os.environ.get('LOGGER_NAME', 'scite_app')
LOG_PATH = os.environ.get('LOG_PATH', 'log/application.log')
LOG_BASENAME = os.path.dirname(LOG_PATH)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(
            log_record,
            record,
            message_dict
        )

        # this doesn't use record.created, so it is slightly off
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        log_record['timestamp'] = now

        log_record['log'] = {
            'level': record.levelname
        }

        if 'name' in log_record:
            log_record['service'] = {
                'name': log_record['name']
            }
            del log_record['name']

        if 'exc_info' in log_record:
            log_record['error'] = log_record.get('error', {})
            log_record['error']['message'] = log_record['exc_info']

        log_record['process'] = {
            'pid': os.getpid()
        }

        log_record['machine'] = {
            'load': os.getloadavg()[0],
            'mem': psutil.virtual_memory().available
        }

        log_record['host'] = log_record.get('host', {})

        log_record['called_by'] = inspect.stack()[-1][1]

        # Assign unique ID to each log for deduplication
        log_record['u_id'] = uuid.uuid4().hex


logger = logging.getLogger(LOGGER_NAME)
formatter = CustomJsonFormatter()


def _create_logger(env=SCITE_ENV):
    logger = logging.getLogger(LOGGER_NAME)
    formatter = CustomJsonFormatter()

    if env == "production":
        os.makedirs(LOG_BASENAME, exist_ok=True)
        log_handler = WatchedFileHandler(LOG_PATH)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)
    else:
        log_handler = StreamHandler(sys.stdout)
        logger.addHandler(log_handler)
        logger.setLevel(logging.DEBUG)

    return logger


logger = _create_logger()
