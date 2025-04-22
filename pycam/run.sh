#!/bin/bash

# Process command line arguments
USE_SQLITE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --sqlite)
      USE_SQLITE=true
      shift
      ;;
    *)
      # Unknown option
      shift
      ;;
  esac
done

# Set database configuration based on choice
if [ "$USE_SQLITE" = true ]; then
  echo "Running with SQLite database"
  export SQLITE=true
else
  echo "Running with PostgreSQL database"
  export SQLITE=false
  # Set PostgreSQL environment variables
  export DB_NAME=pycam_global
  export DB_USER=pycam_user
  export DB_PASSWORD=pycam_password
  export DB_HOST=localhost
  export DB_PORT=5432
fi

# Run with gunicorn using our config
gunicorn pycam.wsgi:application --config=gunicorn_config.py
