#!/bin/bash
set -e

echo "Starting Star Burger application..."

# Ждем доступности PostgreSQL
echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Выполнить миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Собрать статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."

# Выполнить переданные команды
exec "$@"
