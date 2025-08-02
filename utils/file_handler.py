import os
import csv
import requests
import json
import time
from datetime import datetime
from functools import lru_cache
from config import NIFTY50_URL, RETRY_ATTEMPTS, RETRY_DELAY_SEC

class FileHandler:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def create_folders_if_not_exist(self, subfolders):
        os.makedirs(self.data_dir, exist_ok=True)
        for folder in subfolders:
            os.makedirs(os.path.join(self.data_dir, folder), exist_ok=True)

    def get_latest_date_from_indice(self):
        indice_dir = os.path.join(self.data_dir, "indice")
        if not os.path.exists(indice_dir): return None

        latest_date = None
        for filename in os.listdir(indice_dir):
            if filename.endswith('.csv'):
                try:
                    date_str = filename.split('_')[-1].split('.')[0]
                    date = datetime.strptime(date_str, '%d%m%Y')
                    latest_date = max(latest_date, date) if latest_date else date
                except ValueError:
                    continue
        return latest_date.strftime('%d%m%Y') if latest_date else None

    @lru_cache(maxsize=1)
    def download_nifty50_list(self):
        path = os.path.join(self.data_dir, "broad", "nifty50list.csv")
        if not os.path.exists(path):
            response = requests.get(NIFTY50_URL)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(response.text)
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            return [row['Symbol'] for row in reader]

    def download_file(self, url, filepath):
        for attempt in range(RETRY_ATTEMPTS):
            response = requests.get(url)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(response.text)
                return
            time.sleep(RETRY_DELAY_SEC)
        raise Exception(f"Failed to download after {RETRY_ATTEMPTS} attempts: {url}")

    def update_progress(self, progress):
        path = os.path.join(self.data_dir, "progress.json")
        with open(path, 'w') as f:
            json.dump(progress, f)
