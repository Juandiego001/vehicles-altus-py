#!/bin/bash
# Program in bash made to execute with crontab daily at 11:00 pm.
# It is indicated that it will take the previous day.

# Set PROJECT_DIR
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set environment variables
source "$PROJECT_DIR/.env"

# Go to PROJECT_DIR
cd "$PROJECT_DIR"

# Activate python virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Get date
execution_date=$(date '+%d-%m-%Y')

# Execute scraper mode with today's date
python "$PROJECT_DIR/run.py" -ds "$execution_date" -du "$execution_date" -s

# Deactivate python virtual environment
deactivate
