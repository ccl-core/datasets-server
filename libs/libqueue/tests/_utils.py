import os

from libutils.utils import get_str_value

DEFAULT_MONGO_QUEUE_DATABASE: str = "datasets_preview_queue_test"
DEFAULT_MONGO_URL: str = "mongodb://localhost:27018"

MONGO_QUEUE_DATABASE = get_str_value(d=os.environ, key="MONGO_QUEUE_DATABASE", default=DEFAULT_MONGO_QUEUE_DATABASE)
MONGO_URL = get_str_value(d=os.environ, key="MONGO_URL", default=DEFAULT_MONGO_URL)
