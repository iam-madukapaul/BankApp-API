#!/bin/bash

set -o errexit
set -o nounset

if [ "${DJANGO_ENV:-local}" = "local" ]; then
    exec watchfiles 'celery -A config.celery_app worker -l INFO' --filter python
else
    exec celery -A config.celery_app worker -l INFO
fi
