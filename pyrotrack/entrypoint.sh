#!/bin/bash

# Wait for the database to be ready
sleep 5 # TODO: Replace with a proper healthcheck

# Run Django management commands
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic --noinput

# Check if the superuser exists before attempting to create it
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); \
    exists = User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists(); \
    import sys; sys.exit(0) if exists else sys.exit(1);" || \
    python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
fi

# Start the Gunicorn server
gunicorn --bind 0.0.0.0:8000 pyrotrack.wsgi:application
