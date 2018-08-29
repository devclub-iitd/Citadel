#!/bin/bash

echo "Script starts"

python manage.py makemigrations books
python manage.py migrate
python manage.py crontab add
python manage.py collectstatic --noinput
gunicorn bookShelf.wsgi:application --bind 0.0.0.0:8000 --workers 3

echo "Script complete"

exec "$@"
