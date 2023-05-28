
import logging

LOG_FORMAT = "%(message)s"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)