#!/bin/bash
# Быстрый скрипт для локального деплоя (пересборка и рестарт)

set -e

COMPOSE_FILE="${1:-docker-compose.yml}"
COMPOSE_PROJECT="${2:-starburger}"

echo "🔄 Локальный деплой..."
echo "Файл конфига: $COMPOSE_FILE"
echo "Проект: $COMPOSE_PROJECT"

docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" down || true

echo "📦 Пересборка образов..."
docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" build --no-cache

echo "🚀 Запуск контейнеров..."
docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" up -d

echo "⏳ Ожидание инициализации БД..."
sleep 5

echo "✨ Дополнительные команды..."
docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T backend python manage.py migrate --noinput
docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T backend python manage.py collectstatic --noinput

echo ""
echo "✅ Деплой завершен!"
echo ""
docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" ps
echo ""
echo "🌐 Приложение доступно по адресу: http://localhost:8000"
