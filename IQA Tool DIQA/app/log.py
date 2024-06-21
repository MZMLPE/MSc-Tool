import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

LOG = logger.info
WARNING = logger.warning