#!/bin/sh

set -e

echo "Applying migrations..."
python manage.py migrate --noinput

if [ ${AUTO_EXPORT_FIXTURE} ]
then
    echo "Load fixture..."
    python manage.py loaddata fixtures/data.json
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"