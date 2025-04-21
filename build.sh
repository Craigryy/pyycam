#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Poetry
pip install poetry==1.6.1

# Install required additional packages for Gunicorn and production
pip install gevent dj-database-url cloudinary django-cloudinary-storage numpy uvicorn

# Install dependencies
cd pycam
poetry config virtualenvs.create false
poetry install --only main --no-interaction --no-ansi

# Run migrations
python manage.py collectstatic --noinput
python manage.py migrate

# Update Site configuration
python manage.py update_site

# Create superuser
python manage.py shell << EOF
from django.contrib.auth.models import User
user, created = User.objects.get_or_create(username='devadmin', defaults={'email': 'admin@example.com', 'is_superuser': True, 'is_staff': True})
if created:
    user.set_password('nimda')
    user.save()
    print("Superuser 'devadmin' created.")
else:
    print("Superuser 'devadmin' already exists.")
EOF
