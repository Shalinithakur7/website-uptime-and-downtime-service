🛰️ Uptime Monitor Pro - A Multi-Location Website Monitoring System
A lightweight, powerful, and cost-free website uptime monitoring dashboard built with Python, Flask, and the magic of GitHub Actions. This project provides a real-time view of your websites' availability and performance from different geographical locations without requiring any paid servers.


✨ Key Features
This project is designed to be a fully-functional uptime monitoring service with the following features implemented:

Multi-Location Checks: ✅ Leverages GitHub Actions to monitor your sites from both the USA 🇺🇸 and Europe 🇪🇺 simultaneously.

Real-time Dashboard: ✅ A clean, dark-themed dashboard built with Flask and Tailwind CSS to visualize status and historical data.

Historical Data & Charts: ✅ View response time history for each site in beautiful, interactive charts powered by Chart.js.

Cost-Free Architecture: ✅ The entire system is designed to run on the free tiers of GitHub and PythonAnywhere. No costs involved! 💸

Simple & Lightweight: ✅ Uses a simple SQLite database and a minimal Python backend, making it easy to understand and deploy.

🛠️ Technology Stack
This project uses a modern, serverless-first approach to achieve its goals.

Backend: Python & Flask

Serves the web dashboard and acts as the central API to collect monitoring data.

Frontend: HTML, Tailwind CSS, Chart.js

Creates a beautiful, responsive, and interactive user interface.

Database: SQLite

A simple, file-based database to store URLs and check results.

Monitoring Engine: GitHub Actions

The "magic" component that acts as our distributed, serverless checker, running on a 5-minute schedule. 🤖

Deployment: PythonAnywhere

The ideal free hosting platform for this project due to its persistent filesystem for the SQLite database.

⚙️ How It Works - The Architecture
The project's architecture is its most clever feature. It avoids the need for paid, distributed servers by separating the "checker" from the "dashboard".

The Dashboard (PythonAnywhere): A Flask web application is hosted on PythonAnywhere. Its only job is to display the data and listen for incoming reports at a secret /report endpoint.

The Checker (GitHub Actions): A scheduled workflow runs every 5 minutes on GitHub's servers.

Multi-Location Probing: The workflow uses a matrix strategy to run the check script on two different operating systems (ubuntu-latest & windows-latest), which are located in different parts of the world.

Reporting Back: Each checker script pings all the websites listed in the database and sends the results (status, response time, location) back to the Flask app's secure endpoint.

This approach provides a powerful, distributed monitoring system with zero hosting costs.

🚀 Getting Started
To deploy your own instance of the Uptime Monitor, follow these steps:

Clone the Repository:

git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name

Run Locally (Optional but Recommended):

Set up a Python virtual environment.

Install dependencies: pip install -r requirements.txt

Run the app: python app.py

Visit http://127.0.0.1:5000 to test.

Deploy to PythonAnywhere:

Create a free account on PythonAnywhere.

Upload/clone your code.

Configure a new Flask web app, pointing it to your app.py file.

Configure GitHub Secrets:

In your GitHub repository, go to Settings > Secrets and variables > Actions.

Add two secrets:

REPORT_URL: Your live PythonAnywhere app's report endpoint (e.g., http://your-username.pythonanywhere.com/report).

API_SECRET_KEY: The secret key you defined in app.py.

The GitHub Action will now run automatically and populate your live dashboard with data!
