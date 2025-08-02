from flask import Flask, jsonify, request
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from utils.file_handler import FileHandler
from utils.date_utils import DateUtils
from utils.decorators import handle_api_errors
from config import DATA_DIR, SUBFOLDERS, MAX_WORKERS
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

file_handler = FileHandler(DATA_DIR)
date_utils = DateUtils()

@app.route('/api/download-data', methods=['POST'])
@handle_api_errors
def download_data():
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
        progress.update({"current": idx + 1, "status": f"Downloading for {date}"})
        file_handler.update_progress(progress)
        logger.info(f"Processing date: {date}")

        try:
            start_time = time.time()
            file_handler.bulk_download_for_date(date, formatted, formatted_ma)
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for stock in nifty50_list:
                    executor.submit(file_handler.save_yf_5min_data, stock, date, formatted)
            success_dates.append(date)
            progress["status"] = f"Completed {date} in {time.time() - start_time:.2f}s"
        except Exception as e:
            logger.error(f"Error processing {date}: {str(e)}")
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

@app.route('/api/check-folders', methods=['GET'])
@handle_api_errors
def check_folders():
    file_handler.create_folders_if_not_exist(SUBFOLDERS)
    latest = file_handler.get_latest_date_from_indice()
    return jsonify({"lastDownloadDate": latest or "No data found"})

@app.route('/api/progress', methods=['GET'])
@handle_api_errors
def get_progress():
    path = os.path.join(DATA_DIR, "progress.json")
    if not os.path.exists(path):
        return jsonify({"current": 0, "total": 0, "status": "Idle"})
    with open(path, 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API running"})

@app.route('/api/stats', methods=['GET'])
@handle_api_errors
def get_stats():
    return jsonify(file_handler.get_data_stats())

if __name__ == "__main__":
    logger.info("🚀 Starting NSE Data Downloader API...")
    app.run(debug=False, host="0.0.0.0", port=5000)