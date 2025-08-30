import sqlite3
import requests
import os
import json
import platform
from datetime import datetime

# --- Configuration ---
# The database file is expected to be in the same directory
DB_FILE = 'uptime_monitor.db'

# Secrets are securely passed in as environment variables by the GitHub Action
API_KEY = os.environ.get('API_SECRET_KEY')
REPORT_URL = os.environ.get('REPORT_URL')

def get_urls_from_db():
    """Fetches the list of URLs to be monitored from the SQLite database."""
    urls = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Fetch all URLs from the monitored_urls table
        cursor.execute("SELECT id, url FROM monitored_urls")
        urls = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    return urls

def check_url(url):
    """
    Performs an HTTP HEAD request to check the status and response time of a URL.
    Returns a dictionary with the check result.
    """
    try:
        # We use a HEAD request because it's faster. We only need the headers, not the full page content.
        # We set a timeout to prevent the script from hanging on unresponsive sites.
        response = requests.head(url, timeout=10)
        
        # Check if the status code is in the successful range (2xx or 3xx)
        is_up = 200 <= response.status_code < 400
        
        # Response time in milliseconds
        response_time_ms = response.elapsed.total_seconds() * 1000
        
        return {
            'is_up': is_up,
            'status_code': response.status_code,
            'response_time': response_time_ms
        }
    except requests.exceptions.RequestException as e:
        # This catches timeouts, connection errors, etc.
        print(f"Error checking {url}: {e}")
        return {
            'is_up': False,
            'status_code': None,
            'response_time': None
        }

def main():
    """
    Main function to orchestrate the checking and reporting process.
    """
    if not API_KEY or not REPORT_URL:
        print("Error: API_SECRET_KEY and REPORT_URL environment variables are not set.")
        return

    print("Starting uptime checks...")
    urls_to_check = get_urls_from_db()
    
    if not urls_to_check:
        print("No URLs found in the database to check.")
        return

    results = []
    # Determine the location based on the OS of the GitHub Runner
    location = platform.system().lower() # Will be 'linux' or 'windows'

    for url_id, url in urls_to_check:
        print(f"Checking {url} from {location}...")
        result = check_url(url)
        results.append({
            'url_id': url_id,
            'is_up': result['is_up'],
            'status_code': result['status_code'],
            'response_time': result['response_time'],
            'location': location,
            'checked_at': datetime.utcnow().isoformat()
        })
    
    print(f"\nFinished checks. Preparing to send {len(results)} results to the dashboard.")

    # Prepare the final payload to send to our Flask app
    payload = {
        'checks': results
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }

    try:
        # Send the data back to our main application's /report endpoint
        response = requests.post(REPORT_URL, headers=headers, data=json.dumps(payload), timeout=20)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        print("Successfully reported results to the dashboard!")
        print(f"Response from server: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error reporting results to the dashboard: {e}")

if __name__ == "__main__":
    main()

