#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Poetry
pip install poetry==1.6.1

# Install required additional packages for Gunicorn and production
pip install gevent dj-database-url cloudinary django-cloudinary-storage

# Install dependencies
cd pycam
poetry config virtualenvs.create false
poetry install --only main --no-interaction --no-ansi

# Run migrations
python manage.py collectstatic --noinput
python manage.py migrate
