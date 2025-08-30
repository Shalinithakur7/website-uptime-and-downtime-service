-- schema.sql
-- This file defines the structure of the database for the Uptime Monitor.

-- Drop existing tables to ensure a clean slate on initialization.
-- This is useful for development and prevents errors if the schema changes.
DROP TABLE IF EXISTS monitored_urls;
DROP TABLE IF EXISTS checks;

-- Create the table to store the URLs that the user wants to monitor.
-- This table holds the core configuration for each site.
CREATE TABLE monitored_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE, -- The URL itself must be unique to avoid duplicates.
    status TEXT NOT NULL DEFAULT 'pending', -- Can be 'pending', 'up', or 'down'.
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP
);

-- Create the table to store the historical results of each individual uptime check.
-- This table will log every check performed by the GitHub Action.
CREATE TABLE checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL, -- This links back to the monitored_urls table.
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_up BOOLEAN NOT NULL, -- A simple true/false for whether the site was up.
    response_time INTEGER, -- Stored in milliseconds for accuracy.
    status_code INTEGER, -- The HTTP status code (e.g., 200 for OK, 503 for error).
    location TEXT, -- This is where we store the origin of the check (e.g., 'ubuntu-latest').
    FOREIGN KEY (url_id) REFERENCES monitored_urls (id) -- This enforces the link between the two tables.
);

