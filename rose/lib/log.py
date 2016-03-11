import os
import path
import logging
from logging.config import fileConfig

log_path = os.path.join(path.ETC_PATH, 'dev_log.conf')
fileConfig(log_path)

logger = logging.getLogger('simple')