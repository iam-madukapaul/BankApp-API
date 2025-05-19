#!/bin/bash

set -o errexit
set -o nounset

exec watchfiles \
  "celery -A config.celery_app flower \
  --loglevel=info \
  --broker=${CELERY_BROKER_URL} \
  --basic_auth=${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}" \
  --filter python
