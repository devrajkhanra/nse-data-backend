from flask import Flask, jsonify, request
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from utils.file_handler import FileHandler
from utils.date_utils import DateUtils
from config import DATA_DIR, SUBFOLDERS
import os, json, time
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

app = Flask(__name__)
CORS(app)

file_handler = FileHandler(DATA_DIR)
date_utils = DateUtils()

def fetch_yf_5min_data(ticker, target_date):
    start_dt = datetime.strptime(target_date, '%Y-%m-%d')
    end_dt = start_dt + timedelta(days=1)
    df = yf.Ticker(ticker).history(interval="5m", start=start_dt, end=end_dt)
    if df.empty or 'Close' not in df.columns:
        return None
    df.index += pd.Timedelta(hours=5, minutes=30)
    return df[df.index.date == start_dt.date()].reset_index()

def save_5min_data(stock, date, formatted):
    folder = os.path.join(DATA_DIR, "5min", stock)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{formatted}.csv")
    if os.path.exists(file_path): return
    ticker = f"{stock}.NS"
    df = fetch_yf_5min_data(ticker, date)
    if df is not None:
        df.to_csv(file_path, index=False)

@app.route('/api/download-data', methods=['POST'])
def download_data():
    try:
        data = request.json
        if not data or 'type' not in data or 'dates' not in data:
            return jsonify({"error": "Invalid request"}), 400

        date_type, dates_input = data['type'], data['dates']
        dates = [dates_input] if date_type == "single" else (
            date_utils.get_date_range(*dates_input) if date_type == "range" else None
        )
        if not dates:
            return jsonify({"error": "Invalid type or date format"}), 400

        progress = {"current": 0, "total": len(dates), "status": "Starting"}
        file_handler.update_progress(progress)

        nifty50_list = file_handler.download_nifty50_list()
        if not nifty50_list:
            return jsonify({"error": "Could not fetch Nifty50 list"}), 500

        success_dates, failed_dates = [], []

        for idx, date in enumerate(dates):
            formatted = date_utils.format_date(date, 'ddmmyyyy')
            formatted_ma = date_utils.format_date(date, 'ddmmyy')
            progress.update({"current": idx, "status": f"Downloading for {date}"})
            file_handler.update_progress(progress)

            try:
                file_handler.download_file(
                    f"https://archives.nseindia.com/content/indices/ind_close_all_{formatted}.csv",
                    os.path.join(DATA_DIR, "indice", f"ind_close_all_{formatted}.csv")
                )
                file_handler.download_file(
                    f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted}.csv",
                    os.path.join(DATA_DIR, "stock", f"sec_bhavdata_full_{formatted}.csv")
                )
                file_handler.download_file(
                    f"https://archives.nseindia.com/archives/equities/mkt/MA{formatted_ma}.csv",
                    os.path.join(DATA_DIR, "ma", f"MA{formatted_ma}.csv")
                )

                with ThreadPoolExecutor(max_workers=8) as executor:
                    for stock in nifty50_list:
                        executor.submit(save_5min_data, stock, date, formatted)

                success_dates.append(date)
                progress["status"] = f"Completed {date}"
                file_handler.update_progress(progress)

            except Exception as e:
                failed_dates.append({"date": date, "error": str(e)})
                progress["status"] = f"Error on {date}: {str(e)}"
                file_handler.update_progress(progress)

        progress.update({
            "current": len(dates),
            "status": f"Done. Success: {len(success_dates)}, Failed: {len(failed_dates)}"
        })
        file_handler.update_progress(progress)

        return jsonify({
            "status": "completed",
            "successDates": success_dates,
            "failedDates": failed_dates,
            "successCount": len(success_dates),
            "failedCount": len(failed_dates)
        })

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/check-folders', methods=['GET'])
def check_folders():
    try:
        file_handler.create_folders_if_not_exist(SUBFOLDERS)
        latest = file_handler.get_latest_date_from_indice()
        return jsonify({"lastDownloadDate": latest or "No data found"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress', methods=['GET'])
def get_progress():
    try:
        path = os.path.join(DATA_DIR, "progress.json")
        return jsonify(json.load(open(path))) if os.path.exists(path) else jsonify({"current": 0, "total": 0, "status": "Idle"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API running"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = {
            "indice_files": 0,
            "stock_files": 0,
            "ma_files": 0,
            "fivemin_stocks": 0,
            "fivemin_files": 0,
            "total_size_mb": 0
        }

        for subfolder in SUBFOLDERS:
            folder_path = os.path.join(DATA_DIR, subfolder)
            if subfolder == "5min" and os.path.exists(folder_path):
                for stock_dir in os.listdir(folder_path):
                    stock_path = os.path.join(folder_path, stock_dir)
                    if os.path.isdir(stock_path):
                        stats["fivemin_stocks"] += 1
                        stats["fivemin_files"] += len([
                            f for f in os.listdir(stock_path) if f.endswith(".csv")
                        ])
            elif os.path.exists(folder_path):
                stats[f"{subfolder}_files"] = len([
                    f for f in os.listdir(folder_path) if f.endswith(".csv")
                ])

        total_bytes = sum(
            os.path.getsize(os.path.join(root, file))
            for root, _, files in os.walk(DATA_DIR)
            for file in files if file.endswith(".csv")
        )
        stats["total_size_mb"] = int(round(total_bytes / (1024 * 1024), 0))

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting NSE Data Downloader API...")
    app.run(debug=True, host="0.0.0.0", port=5000)
