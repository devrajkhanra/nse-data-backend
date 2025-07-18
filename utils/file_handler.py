# import os
# import csv
# import requests
# from datetime import datetime
# import json

# class FileHandler:
#     def create_folders_if_not_exist(self, base_dir, subfolders):
#         if not os.path.exists(base_dir):
#             os.makedirs(base_dir)
#         for folder in subfolders:
#             folder_path = os.path.join(base_dir, folder)
#             os.makedirs(folder_path, exist_ok=True)
#             if folder == "5min":
#                 # Create subfolders for stocks (will be populated later)
#                 pass

#     def get_latest_date_from_indice(self):
#         indice_dir = os.path.join(os.path.expanduser("~/Desktop/data"), "indice")
#         if not os.path.exists(indice_dir):
#             return None
        
#         latest_date = None
#         for filename in os.listdir(indice_dir):
#             if filename.endswith('.csv'):
#                 try:
#                     date_str = filename.split('_')[-1].split('.')[0]
#                     date = datetime.strptime(date_str, '%d%m%Y')
#                     if not latest_date or date > latest_date:
#                         latest_date = date
#                 except ValueError:
#                     continue
        
#         return latest_date.strftime('%d%m%Y') if latest_date else None

#     def download_nifty50_list(self):
#         url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
#         response = requests.get(url)
#         if response.status_code == 200:
#             with open(os.path.join(os.path.expanduser("~/Desktop/data"), "broad", "nifty50list.csv"), 'w') as f:
#                 f.write(response.text)
#             return [row['Symbol'] for row in csv.DictReader(response.text.splitlines())]
#         return None

#     def download_file(self, url, filepath):
#         response = requests.get(url)
#         if response.status_code == 200:
#             os.makedirs(os.path.dirname(filepath), exist_ok=True)
#             with open(filepath, 'w') as f:
#                 f.write(response.text)
#         else:
#             raise Exception(f"Failed to download {url}, status code: {response.status_code}")

#     def update_progress(self, progress):
#         with open(os.path.join(os.path.expanduser("~/Desktop/data"), "progress.json"), 'w') as f:
#             json.dump(progress, f)

import os
import csv
import requests
from datetime import datetime
import json

from config import NIFTY50_URL

class FileHandler:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def create_folders_if_not_exist(self, subfolders):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        for folder in subfolders:
            folder_path = os.path.join(self.data_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            if folder == "5min":
                # Subfolders for stocks will be created when needed
                pass

    def get_latest_date_from_indice(self):
        indice_dir = os.path.join(self.data_dir, "indice")
        if not os.path.exists(indice_dir):
            return None
        
        latest_date = None
        for filename in os.listdir(indice_dir):
            if filename.endswith('.csv'):
                try:
                    date_str = filename.split('_')[-1].split('.')[0]
                    date = datetime.strptime(date_str, '%d%m%Y')
                    if not latest_date or date > latest_date:
                        latest_date = date
                except ValueError:
                    continue
        
        return latest_date.strftime('%d%m%Y') if latest_date else None

    def download_nifty50_list(self):
        nifty50_path = os.path.join(self.data_dir, "broad", "nifty50list.csv")
        if not os.path.exists(nifty50_path):
            url = NIFTY50_URL
            response = requests.get(url)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(nifty50_path), exist_ok=True)
                with open(nifty50_path, 'w') as f:
                    f.write(response.text)
        with open(nifty50_path, 'r') as f:
            reader = csv.DictReader(f)
            return [row['Symbol'] for row in reader]

    def download_file(self, url, filepath):
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(response.text)
        else:
            raise Exception(f"Failed to download {url}, status code: {response.status_code}")

    def update_progress(self, progress):
        progress_path = os.path.join(self.data_dir, "progress.json")
        with open(progress_path, 'w') as f:
            json.dump(progress, f)