web: cd pycam && gunicorn pycam.wsgi:application --bind 0.0.0.0:$PORT --config gunicorn_config.py
healthcheck: cd pycam && python manage.py db_healthcheck --interval 30
