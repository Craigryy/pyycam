#!/bin/bash

# Set database environment variables
export DB_NAME=pycam_global
export DB_USER=pycam_user
export DB_PASSWORD=pycam_password
export DB_HOST=localhost
export DB_PORT=5432

# Run the Django development server
python manage.py runserver
