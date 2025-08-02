import os
import csv
import requests
import json
import time
from datetime import datetime, timedelta
from functools import lru_cache
from config import NIFTY50_URL, RETRY_ATTEMPTS, RETRY_DELAY_SEC, REQUEST_TIMEOUT, REQUEST_DELAY
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
        self.last_request_time = 0

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
            start_time = time.time()
            start_dt = datetime.strptime(date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=1)
            ticker = yf.Ticker(f"{stock}.NS")
            df = ticker.history(interval="5m", start=start_dt, end=end_dt)
            if not df.empty and "Close" in df.columns:
                df.index += pd.Timedelta(hours=5, minutes=30)  # Adjust to IST
                df[df.index.date == start_dt.date()].reset_index().to_csv(file_path, index=False)
                logger.info(f"Saved 5min data for {stock} on {date} to {file_path} in {time.time() - start_time:.2f}s")
            else:
                logger.warning(f"No data available for {stock} on {date}")
        except Exception as e:
            logger.error(f"Failed to save 5min data for {stock} on {date}: {str(e)}")

    def download_file(self, url, file_path):
        if os.path.exists(file_path):
            logger.info(f"File already exists at {file_path}")
            return True
        # Enforce delay between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - time_since_last)
        start_time = time.time()
        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                self.last_request_time = time.time()
                logger.info(f"Downloaded {url} to {file_path} in {time.time() - start_time:.2f}s")
                return True
            except requests.HTTPError as e:
                if response.status_code == 429:  # Too Many Requests
                    logger.warning(f"Rate limit hit for {url}. Waiting {RETRY_DELAY_SEC * 2}s")
                    time.sleep(RETRY_DELAY_SEC * 2)
                else:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                    if attempt < RETRY_ATTEMPTS - 1:
                        time.sleep(RETRY_DELAY_SEC)
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY_SEC)
            if attempt == RETRY_ATTEMPTS - 1:
                logger.error(f"Failed to download {url} after {RETRY_ATTEMPTS} attempts")
                return False
        return False

    def extract_zip(self, zip_path, extract_to):
        try:
            start_time = time.time()
            file_size = os.path.getsize(zip_path) / (1024 * 1024)  # Size in MB
            logger.info(f"Extracting {zip_path} ({file_size:.2f} MB) to {extract_to}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logger.info(f"Extracted {zip_path} to {extract_to} in {time.time() - start_time:.2f}s")
            os.remove(zip_path)  # Remove the ZIP file after extraction
            return True
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to extract {zip_path}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error extracting {zip_path}: {str(e)}")
            return False

    def bulk_download_for_date(self, date, formatted, formatted_ma):
        # Download indice data
        success = self.download_file(
            f"https://archives.nseindia.com/content/indices/ind_close_all_{formatted}.csv",
            os.path.join(self.get_subfolder_path("indice"), f"ind_close_all_{formatted}.csv")
        )
        if not success:
            logger.warning(f"Skipping indice data for {date} due to download failure")

        # Download stock data
        success = self.download_file(
            f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted}.csv",
            os.path.join(self.get_subfolder_path("stock"), f"sec_bhavdata_full_{formatted}.csv")
        )
        if not success:
            logger.warning(f"Skipping stock data for {date} due to download failure")

        # Download market activity data
        success = self.download_file(
            f"https://archives.nseindia.com/archives/equities/mkt/MA{formatted_ma}.csv",
            os.path.join(self.get_subfolder_path("ma"), f"MA{formatted_ma}.csv")
        )
        if not success:
            logger.warning(f"Skipping market activity data for {date} due to download failure")

        # Download and extract options data
        option_zip_url = f"https://archives.nseindia.com/archives/fo/mkt/fo{formatted}.zip"
        option_zip_path = os.path.join(self.get_subfolder_path("option"), f"fo{formatted}.zip")
        option_extract_path = self.get_subfolder_path("option")
        if self.download_file(option_zip_url, option_zip_path):
            if not self.extract_zip(option_zip_path, option_extract_path):
                logger.warning(f"Failed to extract options data for {date}")
        else:
            logger.warning(f"Skipping options data for {date} due to download failure")

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
            if self.download_file(NIFTY50_URL, file_path):
                with open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    return [row['Symbol'] for row in reader]
            return []
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