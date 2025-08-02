NSE Data Downloader API
Overview
The NSE Data Downloader API is a Flask-based Python application designed to download and manage financial data from the National Stock Exchange of India (NSE). It fetches historical data for Nifty50 stocks, indices, market activity reports, and options data, storing them in a structured directory. The API supports downloading data for single dates or date ranges, fetching 5-minute interval stock data via Yahoo Finance, and extracting options data from ZIP files. It includes robust error handling, progress tracking, and logging to ensure reliable operation.
Features

Data Types:
Indices: Daily closing data for all indices (ind*close_all*[ddmmyyyy].csv).
Stocks: Daily bhavcopy data (sec*bhavdata_full*[ddmmyyyy].csv).
Market Activity: Daily market activity reports (MA[ddmmyy].csv).
Options: Daily options data extracted from ZIP files (fo[ddmmyyyy].zip).
5-Minute Stock Data: Intraday 5-minute data for Nifty50 stocks via Yahoo Finance.

API Endpoints: Download data, check folder status, monitor progress, view stats, and perform health checks.
Error Handling: Robust error handling with retries and logging for failed downloads.
Progress Tracking: Real-time progress updates stored in progress.json.
Rate-Limit Mitigation: Delays between requests and reduced concurrent workers to avoid server throttling.
Logging: Detailed logs for debugging and performance monitoring.

Prerequisites

Python: Version 3.8 or higher.
Operating System: Linux, macOS, or Windows.
Internet Connection: Stable connection for downloading data from NSE and Yahoo Finance.
Disk Space: Sufficient space for storing CSV and extracted ZIP files (options data can be large).
Dependencies: Listed in requirements.txt (see Installation).

Installation

Clone the Repository (or create the project structure manually):
git clone <repository-url>
cd nse-data-downloader

Set Up a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows

Install Dependencies:
pip install -r requirements.txt

The requirements.txt includes:
flask==2.3.3
flask-cors==4.0.0
yfinance==0.2.40
pandas==2.2.2
requests==2.32.3

Note: The zipfile module is part of Python’s standard library and requires no installation.

Verify Directory Structure:Ensure the project has the following structure:
nse-data-downloader/
├── config.py
├── app.py
├── requirements.txt
├── utils/
│ ├── **init**.py
│ ├── file_handler.py
│ ├── date_utils.py
│ ├── decorators.py

Create an empty **init**.py if it doesn’t exist:
touch utils/**init**.py

Configure Data Directory:

The default data directory is ~/Desktop/nse-data/data/. Ensure you have write permissions.
To change the directory, edit BASE_DIR in config.py.

Running the Application

Start the Flask Server:
python app.py

The server runs on http://localhost:5000 by default.
Logs will appear in the console, indicating the API is running (🚀 Starting NSE Data Downloader API...).

Verify the API:Test the health endpoint:
curl http://localhost:5000/api/health

Expected response:
{"status": "healthy", "message": "API running"}

API Endpoints

1. POST /api/download-data
   Downloads data for specified dates, including indices, stocks, market activity, options, and 5-minute stock data.
   Request Body:
   {
   "type": "single" | "range",
   "dates": "YYYY-MM-DD" | ["YYYY-MM-DD", "YYYY-MM-DD"]
   }

type: "single" for one date or "range" for a date range.
dates: A single date string (e.g., "2024-12-31") for single, or a list of start and end dates (e.g., ["2024-12-30", "2024-12-31"]) for range.

Example:
curl -X POST -H "Content-Type: application/json" -d '{"type": "single", "dates": "2024-12-31"}' http://localhost:5000/api/download-data

Response:
{
"status": "completed",
"successDates": ["2024-12-31"],
"failedDates": [],
"successCount": 1,
"failedCount": 0
}

2. GET /api/check-folders
   Creates necessary subfolders and returns the latest date with indice data.
   Example:
   curl http://localhost:5000/api/check-folders

Response:
{"lastDownloadDate": "31122024"}

Or {"lastDownloadDate": "No data found"} if no data exists. 3. GET /api/progress
Returns the current download progress from progress.json.
Example:
curl http://localhost:5000/api/progress

Response:
{
"current": 1,
"total": 2,
"status": "Downloading for 2024-12-31"
}

4. GET /api/health
   Checks if the API is running.
   Example:
   curl http://localhost:5000/api/health

Response:
{"status": "healthy", "message": "API running"}

5. GET /api/stats
   Returns the count of CSV files in each folder and the number of stocks in the 5min folder.
   Example:
   curl http://localhost:5000/api/stats

Response:
{
"indice": 10,
"stock": 10,
"ma": 10,
"option": 15,
"5min_stocks": 50
}

Configuration
The config.py file contains key settings:

BASE_DIR: Root directory (~/Desktop/nse-data).
DATA_DIR: Data storage directory (~/Desktop/nse-data/data).
LOG_DIR: Log storage directory (~/Desktop/nse-data/logs).
SUBFOLDERS: Folders for data storage (["broad", "indice", "ma", "stock", "5min", "option"]).
NIFTY50_URL: URL for the Nifty50 stock list (https://archives.nseindia.com/content/indices/ind_nifty50list.csv).
RETRY_ATTEMPTS: Number of retries for failed downloads (5).
RETRY_DELAY_SEC: Delay between retries (5 seconds).
REQUEST_TIMEOUT: HTTP request timeout (30 seconds).
REQUEST_DELAY: Delay between consecutive requests (2 seconds).
MAX_WORKERS: Maximum concurrent Yahoo Finance requests (4).
ENABLE_LOGGING: Enable/disable logging (True).

To customize, edit config.py. For example, to change the data directory:
BASE_DIR = "/path/to/new/directory"
DATA_DIR = os.path.join(BASE_DIR, "data")

Data Storage
Data is stored in ~/Desktop/nse-data/data/ with the following structure:

broad/: Unused (placeholder for future data types).
indice/: Index data (ind*close_all*[ddmmyyyy].csv).
ma/: Market activity reports (MA[ddmmyy].csv).
stock/: Bhavcopy data (sec*bhavdata_full*[ddmmyyyy].csv).
5min/: 5-minute stock data, organized by stock symbol (e.g., 5min/RELIANCE/[ddmmyyyy].csv).
option/: Extracted options data from ZIP files (e.g., CSV files from fo[ddmmyyyy].zip).
nifty50list.csv: List of Nifty50 stock symbols.
progress.json: Tracks download progress.

How It Works

Initialization:

The Flask app initializes with app.py, setting up endpoints and loading utilities from the utils package.
FileHandler (file_handler.py) manages file downloads and storage.
DateUtils (date_utils.py) handles date formatting and range generation.
handle_api_errors (decorators.py) wraps endpoints for error handling.

Download Process (/api/download-data):

Fetches the Nifty50 stock list from NIFTY50_URL.
For each date:
Downloads indice, stock, market activity, and options data from NSE.
Extracts options ZIP files to the option folder.
Fetches 5-minute stock data for Nifty50 stocks via Yahoo Finance using ThreadPoolExecutor (up to MAX_WORKERS concurrent threads).
Updates progress.json with status.

Skips existing files to avoid redundant downloads.
Logs all operations with timing information.

Rate-Limit Mitigation:

Enforces a REQUEST_DELAY between HTTP requests.
Handles HTTP 429 (Too Many Requests) with extended backoff.
Uses retries (RETRY_ATTEMPTS) for failed downloads.

Error Handling:

Failed downloads are logged and skipped, allowing partial success.
Exceptions are caught and returned as JSON with a 500 status code.

Troubleshooting
Common Issues

Server Slowdown:

Cause: NSE or Yahoo Finance rate-limiting.
Solution: Increase REQUEST_DELAY or reduce MAX_WORKERS in config.py. Test with fewer dates or stocks.
Example:REQUEST_DELAY = 5
MAX_WORKERS = 2

Timeout Errors (HTTPSConnectionPool... Read timed out):

Cause: Slow NSE server or network issues.
Solution: Increase REQUEST_TIMEOUT in config.py (e.g., to 60 seconds). Verify URLs in file_handler.py.
Test URL:curl -I https://archives.nseindia.com/archives/fo/mkt/fo31072025.zip

ZIP Extraction Failures:

Cause: Corrupted or invalid ZIP files.
Solution: Check logs for BadZipFile errors. Manually download and inspect the ZIP file. Update the URL in file_handler.py if needed.

Yahoo Finance Data Missing:

Cause: Rate limits or unavailable data.
Solution: Reduce MAX_WORKERS. Test with a single stock:# In file_handler.py, modify download_nifty50_list:
return [row['Symbol'] for row in reader][:1] # Limit to one stock

Disk I/O Bottlenecks:

Cause: Frequent progress.json writes or large ZIP extractions.
Solution: Move DATA_DIR to an SSD. Reduce progress updates by commenting out intermediate update_progress calls in app.py.

Debugging

Check Logs: Review console output for timing and error messages (e.g., Downloaded ... in 2.34s or Rate limit hit for ...).
Test with Historical Data: Use recent trading days (e.g., 2025-07-31) to ensure data availability.
Monitor Resources: Use htop (Linux/macOS) or Task Manager (Windows) to check CPU, memory, and disk usage.
Network Test: Run speedtest-cli to verify internet stability.

Example Usage

Download Data for a Single Date:
curl -X POST -H "Content-Type: application/json" -d '{"type": "single", "dates": "2025-07-31"}' http://localhost:5000/api/download-data

Download Data for a Date Range:
curl -X POST -H "Content-Type: application/json" -d '{"type": "range", "dates": ["2025-07-30", "2025-07-31"]}' http://localhost:5000/api/download-data

Check Progress:
curl http://localhost:5000/api/progress

View Stats:
curl http://localhost:5000/api/stats

Production Considerations

Use a WSGI Server:Replace Flask’s development server with Gunicorn:
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

Restrict CORS:Update CORS in app.py to allow specific origins:
CORS(app, resources={r"/api/\*": {"origins": ["https://your-frontend.com"]}})

Rate Limiting:Add Flask-Limiter to prevent API abuse:
from flask_limiter import Limiter
Limiter(app, key_func=lambda: request.remote_addr, default_limits=["200 per day", "50 per hour"])

File Locking:Use a library like filelock for thread-safe progress.json writes in a multi-user environment.

Backup Data:Regularly back up ~/Desktop/nse-data/data/ to prevent data loss.

Limitations

Future Dates: Data for dates after August 3, 2025, may not exist, causing download failures.
NSE URL Stability: NSE may change archive URLs, requiring updates to file_handler.py.
Yahoo Finance Reliability: The yfinance library may fail for certain stocks or dates due to API limitations.
Large ZIP Files: Options data ZIPs can be large, impacting disk I/O and extraction time.

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature-name).
Commit changes (git commit -m "Add feature").
Push to the branch (git push origin feature-name).
Open a pull request.

License
This project is licensed under the MIT License.
Contact
For issues or feature requests, open an issue on the repository or contact the maintainer at [your-email@example.com].
