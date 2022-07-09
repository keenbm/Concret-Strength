import logging
import logging.handlers
from datetime import datetime
import os


LOG_DIR="project_logs"

CURRENT_TIME_STAMP=  f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

LOG_FILE_NAME=f"log_{CURRENT_TIME_STAMP}.log"
FORMAT='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'

os.makedirs(LOG_DIR,exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR,LOG_FILE_NAME)

logging.basicConfig(level=logging.INFO,
format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
handlers=[logging.FileHandler(LOG_FILE_PATH),
logging.StreamHandler()]
)

## logging.StreamHandler() is for printing logging information in console