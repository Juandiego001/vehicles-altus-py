#!/bin/bash
# Program in bash made to execute with crontab every 5 minutes.
# It is indicated that it will take the previous day.

# Set PROJECT_DIR
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set environment variables
source "$PROJECT_DIR/.env"

# Go to PROJECT_DIR
cd "$PROJECT_DIR"

# Activate python virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Execute scraper mode with today's date
python "$PROJECT_DIR/run.py"

# Deactivate python virtual environment
deactivate
