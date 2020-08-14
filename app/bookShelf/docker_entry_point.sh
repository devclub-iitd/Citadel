#!/bin/bash

echo "Script starts"

until psql $DATABASE_URL -c '\l'; do
	>&2 echo "Postgres is unavailable - sleeping"
	sleep 1
done

python manage.py makemigrations
python manage.py migrate
python manage.py crontab add
python manage.py collectstatic --noinput
#move to .env
./citadel_superuser.sh
echo "Starting WEB Server"
gunicorn bookShelf.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --forwarded-allow-ips="10.17.6.85" \
    --access-logfile - --error-logfile -

echo "Script complete"

exec "$@"
