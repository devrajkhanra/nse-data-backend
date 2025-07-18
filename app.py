# from datetime import datetime
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from utils.file_handler import FileHandler
# from utils.date_utils import DateUtils
# import os

# app = Flask(__name__)
# CORS(app)  # Enable CORS for frontend communication
# file_handler = FileHandler()
# date_utils = DateUtils()

# # Configuration
# DATA_DIR = os.path.expanduser("~/Desktop/data")
# SUBFOLDERS = ["broad", "indice", "ma", "stock", "5min"]

# @app.route('/api/check-folders', methods=['GET'])
# def check_folders():
#     file_handler.create_folders_if_not_exist(DATA_DIR, SUBFOLDERS)
#     latest_date = file_handler.get_latest_date_from_indice()
#     return jsonify({"lastDownloadDate": latest_date if latest_date else "No data found"})

# @app.route('/api/download-data', methods=['POST'])
# def download_data():
#     data = request.json
#     if data is None:
#         return jsonify({"error": "No JSON data provided"}), 400
#     if 'type' not in data:
#         return jsonify({"error": "Missing 'type' in request"}), 400
#     if 'dates' not in data:
#         return jsonify({"error": "Missing 'dates' in request"}), 400
#     date_type = data['type']
#     dates = data['dates']
#     if date_type == 'single':
#         if not isinstance(dates, str):
#             return jsonify({"error": "For single date, 'dates' should be a string"}), 400
#         dates = [dates]
#     elif date_type == 'range':
#         if not isinstance(dates, list) or len(dates) != 2:
#             return jsonify({"error": "For range, 'dates' should be a list of two strings"}), 400
#         start_date, end_date = dates
#         # Validate that start_date and end_date are valid dates
#         try:
#             datetime.strptime(start_date, '%Y-%m-%d')
#             datetime.strptime(end_date, '%Y-%m-%d')
#         except ValueError:
#             return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
#         dates = date_utils.get_date_range(start_date, end_date)
#     else:
#         return jsonify({"error": "Invalid 'type'. Should be 'single' or 'range'"}), 400
    

#     # if date_type == 'single':
#     #     dates = [dates] if isinstance(dates, str) else dates
#     # else:
#     #     # Transform range to list of dates
#     #     start_date, end_date = dates
#     #     dates = date_utils.get_date_range(start_date, end_date)

#     progress = {"current": 0, "total": len(dates), "status": "Starting"}
#     file_handler.update_progress(progress)

#     nifty50_list = file_handler.download_nifty50_list()
#     if not nifty50_list:
#         return jsonify({"error": "Failed to download Nifty 50 list"}), 500

#     success_dates = []
#     for date in dates:
#         try:
#             formatted_date = date_utils.format_date(date, 'ddmmyyyy')
#             short_date = date_utils.format_date(date, 'ddmmyy')

#             # Download indice data
#             file_handler.download_file(
#                 f"https://archives.nseindia.com/content/indices/ind_close_all_{formatted_date}.csv",
#                 os.path.join(DATA_DIR, "indice", f"ind_close_all_{formatted_date}.csv")
#             )

#             # Download stock data
#             file_handler.download_file(
#                 f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted_date}.csv",
#                 os.path.join(DATA_DIR, "stock", f"sec_bhavdata_full_{formatted_date}.csv")
#             )

#             # Download MA data
#             file_handler.download_file(
#                 f"https://archives.nseindia.com/archives/equities/mkt/MA{short_date}.csv",
#                 os.path.join(DATA_DIR, "ma", f"MA{short_date}.csv")
#             )

#             # Download 5min data for each stock in Nifty 50
#             for stock in nifty50_list:
#                 stock_folder = os.path.join(DATA_DIR, "5min", stock)
#                 os.makedirs(stock_folder, exist_ok=True)
#                 file_handler.download_file(
#                     f"https://archives.nseindia.com/archives/equities/bhavcopy/5min/{stock}/{formatted_date}.csv",
#                     os.path.join(stock_folder, f"{formatted_date}.csv")
#                 )

#             success_dates.append(date)
#             progress["current"] += 1
#             progress["status"] = f"Processed {date}"
#             file_handler.update_progress(progress)

#         except Exception as e:
#             progress["status"] = f"Skipped {date} due to error: {str(e)}"
#             file_handler.update_progress(progress)
#             continue

#     return jsonify({"status": "completed", "successDates": success_dates})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from utils.file_handler import FileHandler
# from utils.date_utils import DateUtils
# from config import DATA_DIR, SUBFOLDERS
# import os
# from datetime import datetime
# import yfinance as yf
# import json

# app = Flask(__name__)
# CORS(app)  # Enable CORS for frontend communication
# file_handler = FileHandler(DATA_DIR)
# date_utils = DateUtils()

# @app.route('/api/check-folders', methods=['GET'])
# def check_folders():
#     file_handler.create_folders_if_not_exist(SUBFOLDERS)
#     latest_date = file_handler.get_latest_date_from_indice()
#     return jsonify({"lastDownloadDate": latest_date if latest_date else "No data found"})

# @app.route('/api/download-data', methods=['POST'])
# def download_data():
#     data = request.json
#     if data is None:
#         return jsonify({"error": "No JSON data provided"}), 400
#     if 'type' not in data:
#         return jsonify({"error": "Missing 'type' in request"}), 400
#     if 'dates' not in data:
#         return jsonify({"error": "Missing 'dates' in request"}), 400
#     date_type = data['type']
#     dates_input = data['dates']
    
#     if date_type == 'single':
#         if not isinstance(dates_input, str):
#             return jsonify({"error": "For single date, 'dates' should be a string"}), 400
#         dates = [dates_input]
#     elif date_type == 'range':
#         if not isinstance(dates_input, list) or len(dates_input) != 2:
#             return jsonify({"error": "For range, 'dates' should be a list of two strings"}), 400
#         start_date, end_date = dates_input
#         try:
#             datetime.strptime(start_date, '%Y-%m-%d')
#             datetime.strptime(end_date, '%Y-%m-%d')
#         except ValueError:
#             return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
#         dates = date_utils.get_date_range(start_date, end_date)
#     else:
#         return jsonify({"error": "Invalid 'type'. Should be 'single' or 'range'"}), 400
    
#     # Initialize progress
#     progress = {"current": 0, "total": len(dates), "status": "Starting"}
#     file_handler.update_progress(progress)
    
#     success_dates = []
#     for date in dates:
#         try:
#             formatted_date_ddmmyyyy = date_utils.format_date(date, 'ddmmyyyy')
#             formatted_date_ddmmyy = date_utils.format_date(date, 'ddmmyy')
            
#             # Download indice data
#             indice_url = f"https://archives.nseindia.com/content/indices/ind_close_all_{formatted_date_ddmmyyyy}.csv"
#             indice_path = os.path.join(DATA_DIR, "indice", f"ind_close_all_{formatted_date_ddmmyyyy}.csv")
#             file_handler.download_file(indice_url, indice_path)
            
#             # Download stock data
#             stock_url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted_date_ddmmyyyy}.csv"
#             stock_path = os.path.join(DATA_DIR, "stock", f"sec_bhavdata_full_{formatted_date_ddmmyyyy}.csv")
#             file_handler.download_file(stock_url, stock_path)
            
#             # Download MA data
#             ma_url = f"https://archives.nseindia.com/content/indices/MA{formatted_date_ddmmyy}.csv"
#             ma_path = os.path.join(DATA_DIR, "ma", f"MA{formatted_date_ddmmyy}.csv")
#             file_handler.download_file(ma_url, ma_path)
            
#             # Download 5min data for each Nifty50 stock
#             nifty50_list = file_handler.download_nifty50_list()
#             for stock in nifty50_list:
#                 stock_folder = os.path.join(DATA_DIR, "5min", stock)
#                 os.makedirs(stock_folder, exist_ok=True)
#                 ticker = f"{stock}.NS"
#                 start_date = datetime.strptime(date, '%Y-%m-%d')
#                 end_date = start_date
#                 try:
#                     stock_data = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="5m")
#                     if not stock_data.empty:
#                         csv_path = os.path.join(stock_folder, f"{formatted_date_ddmmyyyy}.csv")
#                         stock_data.to_csv(csv_path)
#                 except Exception as e:
#                     print(f"Error downloading 5min data for {stock} on {date}: {e}")
#                     # Continue with next stock
            
#             success_dates.append(date)
#             progress["current"] += 1
#             progress["status"] = f"Processed {date}"
#             file_handler.update_progress(progress)
        
#         except Exception as e:
#             progress["status"] = f"Skipped {date} due to error: {str(e)}"
#             file_handler.update_progress(progress)
#             continue
    
#     return jsonify({"status": "completed", "successDates": success_dates})

# @app.route('/api/progress', methods=['GET'])
# def get_progress():
#     progress_path = os.path.join(DATA_DIR, "progress.json")
#     if os.path.exists(progress_path):
#         with open(progress_path, 'r') as f:
#             progress = json.load(f)
#             return jsonify(progress)
#     else:
#         return jsonify({"current": 0, "total": 0, "status": "Idle"})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.file_handler import FileHandler
from utils.date_utils import DateUtils
from config import DATA_DIR, SUBFOLDERS
import os
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import json
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
file_handler = FileHandler(DATA_DIR)
date_utils = DateUtils()

@app.route('/api/check-folders', methods=['GET'])
def check_folders():
    """Check if folders exist and return the latest download date"""
    try:
        file_handler.create_folders_if_not_exist(SUBFOLDERS)
        latest_date = file_handler.get_latest_date_from_indice()
        return jsonify({"lastDownloadDate": latest_date if latest_date else "No data found"})
    except Exception as e:
        return jsonify({"error": f"Error checking folders: {str(e)}"}), 500

@app.route('/api/download-data', methods=['POST'])
def download_data():
    """Download market data for specified dates"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400
        if 'type' not in data:
            return jsonify({"error": "Missing 'type' in request"}), 400
        if 'dates' not in data:
            return jsonify({"error": "Missing 'dates' in request"}), 400
        
        date_type = data['type']
        dates_input = data['dates']
        
        # Process dates based on type
        if date_type == 'single':
            if not isinstance(dates_input, str):
                return jsonify({"error": "For single date, 'dates' should be a string"}), 400
            dates = [dates_input]
        elif date_type == 'range':
            if not isinstance(dates_input, list) or len(dates_input) != 2:
                return jsonify({"error": "For range, 'dates' should be a list of two strings"}), 400
            start_date, end_date = dates_input
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            dates = date_utils.get_date_range(start_date, end_date)
        else:
            return jsonify({"error": "Invalid 'type'. Should be 'single' or 'range'"}), 400
        
        # Initialize progress
        progress = {"current": 0, "total": len(dates), "status": "Starting download process"}
        file_handler.update_progress(progress)
        
        # Download Nifty50 list once at the beginning
        print("Downloading Nifty50 list...")
        nifty50_list = file_handler.download_nifty50_list()
        if not nifty50_list:
            return jsonify({"error": "Failed to download Nifty 50 list"}), 500
        
        success_dates = []
        failed_dates = []
        
        for date_index, date in enumerate(dates):
            try:
                print(f"Processing date: {date} ({date_index + 1}/{len(dates)})")
                
                formatted_date_ddmmyyyy = date_utils.format_date(date, 'ddmmyyyy')
                formatted_date_ddmmyy = date_utils.format_date(date, 'ddmmyy')
                
                # Update progress
                progress["current"] = date_index
                progress["status"] = f"Processing {date} - Downloading indices data"
                file_handler.update_progress(progress)
                
                # Download indice data
                try:
                    indice_url = f"https://archives.nseindia.com/content/indices/ind_close_all_{formatted_date_ddmmyyyy}.csv"
                    indice_path = os.path.join(DATA_DIR, "indice", f"ind_close_all_{formatted_date_ddmmyyyy}.csv")
                    file_handler.download_file(indice_url, indice_path)
                    print(f"Downloaded indice data for {date}")
                except Exception as e:
                    print(f"Failed to download indice data for {date}: {e}")
                
                # Update progress
                progress["status"] = f"Processing {date} - Downloading stock data"
                file_handler.update_progress(progress)
                
                # Download stock data
                try:
                    stock_url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted_date_ddmmyyyy}.csv"
                    stock_path = os.path.join(DATA_DIR, "stock", f"sec_bhavdata_full_{formatted_date_ddmmyyyy}.csv")
                    file_handler.download_file(stock_url, stock_path)
                    print(f"Downloaded stock data for {date}")
                except Exception as e:
                    print(f"Failed to download stock data for {date}: {e}")
                
                # Update progress
                progress["status"] = f"Processing {date} - Downloading MA data"
                file_handler.update_progress(progress)
                
                # Download MA data
                # try:
                #     ma_url = f"https://archives.nseindia.com/content/indices/MA{formatted_date_ddmmyy}.csv"
                #     ma_path = os.path.join(DATA_DIR, "ma", f"MA{formatted_date_ddmmyy}.csv")
                #     file_handler.download_file(ma_url, ma_path)
                #     print(f"Downloaded MA data for {date}")
                # except Exception as e:
                #     print(f"Failed to download MA data for {date}: {e}")
                
                # Update progress
                progress["status"] = f"Processing {date} - Downloading 5min data for {len(nifty50_list)} stocks"
                file_handler.update_progress(progress)
                
                # Download 5min data for each Nifty50 stock
                successful_5min_downloads = 0
                failed_5min_downloads = 0
                
                for stock_index, stock in enumerate(nifty50_list):
                    stock_folder = os.path.join(DATA_DIR, "5min", stock)
                    os.makedirs(stock_folder, exist_ok=True)
                    
                    csv_path = os.path.join(stock_folder, f"{formatted_date_ddmmyyyy}.csv")
                    
                    # Skip if file already exists
                    if os.path.exists(csv_path):
                        print(f"5min data for {stock} on {date} already exists, skipping...")
                        successful_5min_downloads += 1
                        continue
                    
                    # Update progress for individual stocks
                    if stock_index % 10 == 0:  # Update every 10 stocks
                        progress["status"] = f"Processing {date} - Downloading 5min data ({stock_index + 1}/{len(nifty50_list)}) - {stock}"
                        file_handler.update_progress(progress)
                    
                    try:
                        # Method 1: Try NSE archives first (multiple URL patterns)
                        # downloaded_from_nse = False
                        # possible_urls = [
                        #     f"https://archives.nseindia.com/archives/equities/bhavcopy/5min/{stock}/{formatted_date_ddmmyyyy}.csv",
                        #     f"https://archives.nseindia.com/content/historical/EQUITIES/5min/{stock}/{formatted_date_ddmmyyyy}.csv",
                        #     f"https://archives.nseindia.com/products/content/5min/{stock}_{formatted_date_ddmmyyyy}.csv"
                        # ]
                        
                        # for url in possible_urls:
                        #     try:
                        #         file_handler.download_file(url, csv_path)
                        #         print(f"Successfully downloaded 5min data for {stock} from NSE archives")
                        #         downloaded_from_nse = True
                        #         successful_5min_downloads += 1
                        #         break
                        #     except Exception:
                        #         continue
                        
                        # if downloaded_from_nse:
                        #     continue
                        
                        # Method 2: Fallback to yfinance
                        ticker = f"{stock}.NS"
                        start_date = datetime.strptime(date, '%Y-%m-%d')
                        end_date = start_date + timedelta(days=1)
                        print(start_date, ' ', end_date)
                        
                        stock_data = yf.download(ticker, start=start_date, end=end_date, interval="5m")
                        
                        # if not stock_data.empty:
                        #     # Filter for the specific date only using string comparison
                        #     target_date_str = start_date.strftime('%Y-%m-%d')
                        #     stock_data = stock_data[stock_data.index.strftime('%Y-%m-%d') == target_date_str]
                            
                        if not stock_data.empty:
                            target_date = pd.Timestamp(start_date).date()
                            stock_data = stock_data[pd.to_datetime(stock_data.index).date == target_date]    
                            if not stock_data.empty:
                                stock_data.to_csv(csv_path)
                                print(f"Successfully downloaded 5min data for {stock} via yfinance")
                                successful_5min_downloads += 1
                            else:
                                print(f"No trading data for {stock} on {date} (weekend/holiday)")
                                failed_5min_downloads += 1
                        else:
                            print(f"No 5min data available for {stock} on {date}")
                            failed_5min_downloads += 1
                            
                    except Exception as e:
                        print(f"Error downloading 5min data for {stock} on {date}: {e}")
                        failed_5min_downloads += 1
                        continue
                    
                    # Add a small delay to avoid rate limiting
                    if stock_index % 10 == 0 and stock_index > 0:
                        time.sleep(0.5)
                
                print(f"5min data summary for {date}: {successful_5min_downloads} successful, {failed_5min_downloads} failed")
                
                success_dates.append(date)
                
                # Update progress after completing the date
                progress["current"] = date_index + 1
                progress["status"] = f"Completed {date} - {successful_5min_downloads}/{len(nifty50_list)} 5min files downloaded"
                file_handler.update_progress(progress)
                
            except Exception as e:
                print(f"Error processing date {date}: {e}")
                failed_dates.append({"date": date, "error": str(e)})
                progress["current"] = date_index + 1
                progress["status"] = f"Skipped {date} due to error: {str(e)}"
                file_handler.update_progress(progress)
                continue
        
        # Final progress update
        progress["current"] = len(dates)
        progress["status"] = f"Download completed. Success: {len(success_dates)}, Failed: {len(failed_dates)}"
        file_handler.update_progress(progress)
        
        return jsonify({
            "status": "completed", 
            "successDates": success_dates,
            "failedDates": failed_dates,
            "totalProcessed": len(dates),
            "successCount": len(success_dates),
            "failedCount": len(failed_dates)
        })
    
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get current download progress"""
    try:
        progress_path = os.path.join(DATA_DIR, "progress.json")
        if os.path.exists(progress_path):
            with open(progress_path, 'r') as f:
                progress = json.load(f)
                return jsonify(progress)
        else:
            return jsonify({"current": 0, "total": 0, "status": "Idle"})
    except Exception as e:
        return jsonify({"error": f"Error reading progress: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "NSE Data Downloader API is running"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about downloaded data"""
    try:
        stats = {
            "indice_files": 0,
            "stock_files": 0,
            "ma_files": 0,
            "fivemin_stocks": 0,
            "fivemin_files": 0,
            "total_size_mb": 0
        }
        
        # Count files in each directory
        for subfolder in SUBFOLDERS:
            folder_path = os.path.join(DATA_DIR, subfolder)
            if os.path.exists(folder_path):
                if subfolder == "5min":
                    # Count stock folders and files
                    for stock_folder in os.listdir(folder_path):
                        stock_path = os.path.join(folder_path, stock_folder)
                        if os.path.isdir(stock_path):
                            stats["fivemin_stocks"] += 1
                            stats["fivemin_files"] += len([f for f in os.listdir(stock_path) if f.endswith('.csv')])
                else:
                    file_count = len([f for f in os.listdir(folder_path) if f.endswith('.csv')])
                    stats[f"{subfolder}_files"] = file_count
        
        # Calculate total size (basic implementation)
        total_size = 0
        for root, dirs, files in os.walk(DATA_DIR):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        pass
        
        stats["total_size_mb"] = int(round(total_size / (1024 * 1024), 0))
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Error getting stats: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting NSE Data Downloader API...")
    print(f"Data directory: {DATA_DIR}")
    print(f"Subfolders: {SUBFOLDERS}")
    app.run(debug=True, host='0.0.0.0', port=5000)