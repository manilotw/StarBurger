#!/bin/bash

# Скрипт автоматизированного деплоя на сервер
# Использование: ./deploy.sh [server_host] [server_user]
# Пример: ./deploy.sh example.com root

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Параметры
SERVER_HOST="${1:-localhost}"
SERVER_USER="${2:-root}"
DEPLOY_DIR="/var/www/star-burger"
REPO_URL="https://github.com/your-username/star-burger.git"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Star Burger Deployment Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Server: $SERVER_HOST"
echo "User: $SERVER_USER"
echo "Deploy directory: $DEPLOY_DIR"
echo ""

# Функция для выполнения команд на сервере
run_on_server() {
    ssh "$SERVER_USER@$SERVER_HOST" "cd $DEPLOY_DIR && $1"
}

# Функция для отправки файлов на сервер
upload_file() {
    scp "$1" "$SERVER_USER@$SERVER_HOST:$DEPLOY_DIR/"
}

# Проверка подключения
echo -e "${YELLOW}[1/6]${NC} Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=5 "$SERVER_USER@$SERVER_HOST" "echo 'OK'" > /dev/null 2>&1; then
    echo -e "${RED}Ошибка: Не удается подключиться к серверу${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Подключение успешно${NC}"

# Подготовка на локальной машине
echo ""
echo -e "${YELLOW}[2/6]${NC} Подготовка к деплою..."
git fetch origin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
LATEST_COMMIT=$(git rev-parse HEAD)
COMMIT_MESSAGE=$(git log -1 --pretty=%B)
echo "Branch: $CURRENT_BRANCH"
echo "Latest commit: $LATEST_COMMIT"
echo "Message: $COMMIT_MESSAGE"

# Создание/обновление директории на сервере
echo ""
echo -e "${YELLOW}[3/6]${NC} Обновление кода на сервере..."
run_on_server "
    if [ ! -d '.git' ]; then
        echo 'Инициализация репозитория...'
        git init
        git remote add origin $REPO_URL
    fi
    git fetch origin $CURRENT_BRANCH
    git checkout -f origin/$CURRENT_BRANCH
    git reset --hard origin/$CURRENT_BRANCH
"
echo -e "${GREEN}✓ Код обновлен${NC}"

# Обновление .env файла (опционально)
echo ""
echo -e "${YELLOW}[4/6]${NC} Проверка конфигурации..."
if [ -f ".env.prod" ]; then
    echo "Отправка .env.prod файла..."
    upload_file ".env.prod"
    run_on_server "mv .env.prod .env"
else
    echo -e "${YELLOW}⚠ .env.prod файл не найден локально, используется существующий на сервере${NC}"
fi

# Пересборка и перезапуск контейнеров
echo ""
echo -e "${YELLOW}[5/6]${NC} Пересборка Docker образов и перезапуск приложения..."
run_on_server "
    echo 'Запуск docker-compose...'
    docker-compose -f docker-compose.prod.yml down || true
    docker-compose -f docker-compose.prod.yml up -d --build
    
    echo 'Создание таблиц БД...'
    sleep 5
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --noinput
    
    echo 'Сборка статических файлов...'
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput
"
echo -e "${GREEN}✓ Контейнеры пересобраны и перезапущены${NC}"

# Проверка здоровья приложения
echo ""
echo -e "${YELLOW}[6/6]${NC} Проверка статуса приложения..."
sleep 3

HEALTH_CHECK=$(ssh "$SERVER_USER@$SERVER_HOST" "curl -s http://localhost/health || echo 'FAILED'" 2>/dev/null || echo "FAILED")

if [ "$HEALTH_CHECK" = "healthy" ]; then
    echo -e "${GREEN}✓ Приложение работает корректно${NC}"
else
    echo -e "${YELLOW}⚠ Не удалось проверить здоровье приложения${NC}"
    echo "Статус контейнеров:"
    run_on_server "docker-compose -f docker-compose.prod.yml ps"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Деплой успешно завершен!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Приложение доступно по адресу: http://$SERVER_HOST"
