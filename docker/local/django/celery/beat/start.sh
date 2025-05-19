#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

# Apply migrations for django_celery_beat
python manage.py migrate django_celery_beat

# Remove any existing celerybeat PID file to avoid conflicts
rm -f './celerybeat.pid'

# Start the celery beat process with watchfiles to monitor Python files
exec watchfiles \
  'celery -A config.celery_app beat -l INFO' \
  --filter python
