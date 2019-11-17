#!/usr/bin/env bash

echo "Waiting for MySQL..."

while ! nc -z db 3306; do
  sleep 0.5
done

echo "MySQL started"

# Commands for DB migrations -- Better to do it manually due to the relations!

# flask db init
# echo "Init completed"
# flask db migrate
# echo "Migrate completed"
# flask db upgrade
# echo "Upgrade completed"

cd /home/App
python run.py
