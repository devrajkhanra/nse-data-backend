import os
import csv
import requests
import json
import time
from datetime import datetime, timedelta
from functools import lru_cache
from config import NIFTY50_URL, RETRY_ATTEMPTS, RETRY_DELAY_SEC
import yfinance as yf
import pandas as pd
import zipfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def get_subfolder_path(self, name):
        return os.path.join(self.data_dir, name)

    def create_folders_if_not_exist(self, subfolders):
        os.makedirs(self.data_dir, exist_ok=True)
        for folder in subfolders:
            os.makedirs(self.get_subfolder_path(folder), exist_ok=True)

    def get_latest_date_from_indice(self):
        indice_dir = self.get_subfolder_path("indice")
        if not os.path.exists(indice_dir):
            return None
        latest = None
        for filename in os.listdir(indice_dir):
            if filename.endswith('.csv'):
                try:
                    date_str = filename.split('_')[-1].split('.')[0]
                    date = datetime.strptime(date_str, '%d%m%Y')
                    latest = max(latest, date) if latest else date
                except ValueError:
                    continue
        return latest.strftime('%d%m%Y') if latest else None

    def get_stock_data_path(self, stock, filename):
        folder = self.get_subfolder_path(os.path.join("5min", stock))
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, filename)

    def save_yf_5min_data(self, stock, date, formatted):
        file_path = self.get_stock_data_path(stock, f"{formatted}.csv")
        if os.path.exists(file_path):
            logger.info(f"Data for {stock} on {date} already exists at {file_path}")
            return
        try:
            start_dt = datetime.strptime(date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=1)
            ticker = yf.Ticker(f"{stock}.NS")
            df = ticker.history(interval="5m", start=start_dt, end=end_dt)
            if not df.empty and "Close" in df.columns:
                df.index += pd.Timedelta(hours=5, minutes=30)  # Adjust to IST
                df[df.index.date == start_dt.date()].reset_index().to_csv(file_path, index=False)
                logger.info(f"Saved 5min data for {stock} on {date} to {file_path}")
            else:
                logger.warning(f"No data available for {stock} on {date}")
        except Exception as e:
            logger.error(f"Failed to save 5min data for {stock} on {date}: {str(e)}")

    def download_file(self, url, file_path):
        if os.path.exists(file_path):
            logger.info(f"File already exists at {file_path}")
            return
        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded {url} to {file_path}")
                return
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY_SEC)
                else:
                    logger.error(f"Failed to download {url} after {RETRY_ATTEMPTS} attempts")
                    raise

    def extract_zip(self, zip_path, extract_to):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logger.info(f"Extracted {zip_path} to {extract_to}")
            os.remove(zip_path)  # Remove the ZIP file after extraction
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to extract {zip_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting {zip_path}: {str(e)}")
            raise

    def bulk_download_for_date(self, date, formatted, formatted_ma):
        # Download indice data
        self.download_file(
            f"https://archives.nseindia.com/content/indices/ind_close_all_{formatted}.csv",
            os.path.join(self.get_subfolder_path("indice"), f"ind_close_all_{formatted}.csv")
        )
        # Download stock data
        self.download_file(
            f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted}.csv",
            os.path.join(self.get_subfolder_path("stock"), f"sec_bhavdata_full_{formatted}.csv")
        )
        # Download market activity data
        self.download_file(
            f"https://archives.nseindia.com/archives/equities/mkt/MA{formatted_ma}.csv",
            os.path.join(self.get_subfolder_path("ma"), f"MA{formatted_ma}.csv")
        )
        # Download and extract options data
        option_zip_url = f"https://nsearchives.nseindia.com/archives/fo/mkt/fo{formatted}.zip"
        option_zip_path = os.path.join(self.get_subfolder_path("option"), f"fo{formatted}.zip")
        option_extract_path = self.get_subfolder_path("option")
        self.download_file(option_zip_url, option_zip_path)
        self.extract_zip(option_zip_path, option_extract_path)

    def update_progress(self, progress):
        path = os.path.join(self.data_dir, "progress.json")
        try:
            with open(path, 'w') as f:
                json.dump(progress, f, indent=2)
            logger.info(f"Updated progress: {progress['status']}")
        except Exception as e:
            logger.error(f"Failed to update progress: {str(e)}")

    @lru_cache(maxsize=1)
    def download_nifty50_list(self):
        file_path = os.path.join(self.data_dir, "nifty50list.csv")
        try:
            self.download_file(NIFTY50_URL, file_path)
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                return [row['Symbol'] for row in reader]
        except Exception as e:
            logger.error(f"Failed to download Nifty50 list: {str(e)}")
            return []

    def get_data_stats(self):
        stats = {}
        for folder in ["indice", "stock", "ma", "option"]:
            folder_path = self.get_subfolder_path(folder)
            stats[folder] = len([f for f in os.listdir(folder_path) if f.endswith('.csv')]) if os.path.exists(folder_path) else 0
        stock_folder = self.get_subfolder_path("5min")
        stats["5min_stocks"] = len([d for d in os.listdir(stock_folder) if os.path.isdir(os.path.join(stock_folder, d))]) if os.path.exists(stock_folder) else 0
        return stats