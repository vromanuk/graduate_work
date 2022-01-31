#!/usr/bin/env bash

echo "Postgres is not running..."

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 0.1
done

echo "Postgres is running"

python3 manage.py migrate

exec "$@"
