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

from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.file_handler import FileHandler
from utils.date_utils import DateUtils
from config import DATA_DIR, SUBFOLDERS
import os
from datetime import datetime
import yfinance as yf
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
file_handler = FileHandler(DATA_DIR)
date_utils = DateUtils()

@app.route('/api/check-folders', methods=['GET'])
def check_folders():
    file_handler.create_folders_if_not_exist(SUBFOLDERS)
    latest_date = file_handler.get_latest_date_from_indice()
    return jsonify({"lastDownloadDate": latest_date if latest_date else "No data found"})

@app.route('/api/download-data', methods=['POST'])
def download_data():
    data = request.json
    if data is None:
        return jsonify({"error": "No JSON data provided"}), 400
    if 'type' not in data:
        return jsonify({"error": "Missing 'type' in request"}), 400
    if 'dates' not in data:
        return jsonify({"error": "Missing 'dates' in request"}), 400
    date_type = data['type']
    dates_input = data['dates']
    
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
    progress = {"current": 0, "total": len(dates), "status": "Starting"}
    file_handler.update_progress(progress)
    
    success_dates = []
    for date in dates:
        try:
            formatted_date_ddmmyyyy = date_utils.format_date(date, 'ddmmyyyy')
            formatted_date_ddmmyy = date_utils.format_date(date, 'ddmmyy')
            
            # Download indice data
            indice_url = f"https://archives.nseindia.com/content/indices/ind_close_all_{formatted_date_ddmmyyyy}.csv"
            indice_path = os.path.join(DATA_DIR, "indice", f"ind_close_all_{formatted_date_ddmmyyyy}.csv")
            file_handler.download_file(indice_url, indice_path)
            
            # Download stock data
            stock_url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted_date_ddmmyyyy}.csv"
            stock_path = os.path.join(DATA_DIR, "stock", f"sec_bhavdata_full_{formatted_date_ddmmyyyy}.csv")
            file_handler.download_file(stock_url, stock_path)
            
            # Download MA data
            ma_url = f"https://archives.nseindia.com/content/indices/MA{formatted_date_ddmmyy}.csv"
            ma_path = os.path.join(DATA_DIR, "ma", f"MA{formatted_date_ddmmyy}.csv")
            file_handler.download_file(ma_url, ma_path)
            
            # Download 5min data for each Nifty50 stock
            nifty50_list = file_handler.download_nifty50_list()
            for stock in nifty50_list:
                stock_folder = os.path.join(DATA_DIR, "5min", stock)
                os.makedirs(stock_folder, exist_ok=True)
                ticker = f"{stock}.NS"
                start_date = datetime.strptime(date, '%Y-%m-%d')
                end_date = start_date
                try:
                    stock_data = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="5m")
                    if not stock_data.empty:
                        csv_path = os.path.join(stock_folder, f"{formatted_date_ddmmyyyy}.csv")
                        stock_data.to_csv(csv_path)
                except Exception as e:
                    print(f"Error downloading 5min data for {stock} on {date}: {e}")
                    # Continue with next stock
            
            success_dates.append(date)
            progress["current"] += 1
            progress["status"] = f"Processed {date}"
            file_handler.update_progress(progress)
        
        except Exception as e:
            progress["status"] = f"Skipped {date} due to error: {str(e)}"
            file_handler.update_progress(progress)
            continue
    
    return jsonify({"status": "completed", "successDates": success_dates})

@app.route('/api/progress', methods=['GET'])
def get_progress():
    progress_path = os.path.join(DATA_DIR, "progress.json")
    if os.path.exists(progress_path):
        with open(progress_path, 'r') as f:
            progress = json.load(f)
            return jsonify(progress)
    else:
        return jsonify({"current": 0, "total": 0, "status": "Idle"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)