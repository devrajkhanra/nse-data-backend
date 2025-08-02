import os

BASE_DIR = os.path.expanduser("~/Desktop/nse-data")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

SUBFOLDERS = ["broad", "indice", "ma", "stock", "5min", "option"]
NIFTY50_URL = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"

RETRY_ATTEMPTS = 3
RETRY_DELAY_SEC = 2
ENABLE_LOGGING = True