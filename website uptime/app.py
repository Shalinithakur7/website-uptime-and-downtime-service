import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort

# --- App Setup ---
# This section initializes the Flask application and sets up configuration.
app = Flask(__name__)
app.config['DATABASE'] = 'uptime_monitor.db'
# This is a secret key to ensure only our GitHub Action can post data.
# On a live server like PythonAnywhere, you'll set this as an environment variable for better security.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key_12345')


# --- Database Functions ---
def get_db():
    """Opens a new database connection for a request."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row # This allows accessing columns by name.
    return conn

def init_db():
    """Initializes the database using the schema.sql file."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main dashboard page, showing all monitored URLs."""
    db = get_db()
    monitored_urls = db.execute(
        'SELECT * FROM monitored_urls ORDER BY created_at DESC'
    ).fetchall()
    return render_template('index.html', monitored_urls=monitored_urls)

@app.route('/add', methods=('GET', 'POST'))
def add_url():
    """Handles the form for adding a new URL to the database."""
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        # Ensure the URL has a scheme (http:// or https://)
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        db = get_db()
        db.execute(
            'INSERT INTO monitored_urls (name, url) VALUES (?, ?)',
            (name, url)
        )
        db.commit()
        return redirect(url_for('index')) # Redirect back to the dashboard
    return render_template('add_url.html')

@app.route('/delete/<int:url_id>', methods=('POST',))
def delete_url(url_id):
    """Deletes a monitored URL and all of its associated check history."""
    db = get_db()
    db.execute('DELETE FROM checks WHERE url_id = ?', (url_id,))
    db.execute('DELETE FROM monitored_urls WHERE id = ?', (url_id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/report', methods=['POST'])
def report():
    """
    This is the secure API endpoint that receives uptime data from our GitHub Actions worker.
    """
    # 1. Security Check: Ensure the request includes the correct secret key.
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {app.config['SECRET_KEY']}":
        print("⚠️ Unauthorized access attempt to /report blocked.")
        abort(403) # Forbidden

    # 2. Extract the data from the incoming JSON request.
    data = request.json
    url = data.get('url')
    location = data.get('location')
    is_up = data.get('is_up')
    response_time = data.get('response_time')
    status_code = data.get('status_code')

    if not url:
        return jsonify({"status": "error", "message": "URL missing"}), 400

    # 3. Find the URL in our database and store the check result.
    db = get_db()
    url_row = db.execute('SELECT id FROM monitored_urls WHERE url = ?', (url,)).fetchone()
    
    if url_row:
        url_id = url_row['id']
        db.execute(
            'INSERT INTO checks (url_id, is_up, response_time, status_code, location) VALUES (?, ?, ?, ?, ?)',
            (url_id, is_up, response_time, status_code, location)
        )
        # Also update the latest status on the main URL table
        db.execute(
            'UPDATE monitored_urls SET last_checked = CURRENT_TIMESTAMP, status = ? WHERE id = ?',
            ('up' if is_up else 'down', url_id)
        )
        db.commit()
        print(f"✅ Received report for {url} from {location}")
        return jsonify({"status": "success"})
    else:
        print(f"⚠️ Received report for an unknown URL: {url}")
        return jsonify({"status": "error", "message": "URL not found in database"}), 404


@app.route('/history/<int:url_id>')
def history(url_id):
    """Provides check history as JSON, which is used by the Chart.js library on the frontend."""
    db = get_db()
    url_info = db.execute('SELECT name, url FROM monitored_urls WHERE id = ?', (url_id,)).fetchone()
    
    # This query gets the last 50 checks from each location to create a balanced chart.
    checks_query = """
    SELECT * FROM (
        SELECT *, ROW_NUMBER() OVER(PARTITION BY location ORDER BY checked_at DESC) as rn
        FROM checks
        WHERE url_id = ?
    ) WHERE rn <= 50 ORDER BY checked_at ASC
    """
    checks = db.execute(checks_query, (url_id,)).fetchall()
    
    # Convert database rows to a list of dictionaries for easy JSON conversion.
    checks_data = [dict(row) for row in checks]
    
    return jsonify({
        'name': url_info['name'],
        'url': url_info['url'],
        'checks': checks_data
    })


# This block runs only when you execute "python app.py" directly.
# It will not run on the production server (e.g., PythonAnywhere).
if __name__ == '__main__':
    # Check if the database file exists, and if not, create it.
    if not os.path.exists(app.config['DATABASE']):
        print("Database not found, initializing...")
        init_db()
    # Start the local development server.
    app.run(debug=True, port=5001)

