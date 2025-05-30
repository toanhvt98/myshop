#!/bin/sh

# Chạy migrate trước
python manage.py makemigrations
python manage.py migrate

# Cuối cùng chạy server
exec "$@"
