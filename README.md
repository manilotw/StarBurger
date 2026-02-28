# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

### С использованием Docker Compose (Рекомендуется)

Это самый быстрый и надежный способ развернуть проект на локальной машине.

**Требования:**
- [Docker](https://www.docker.com/products/docker-desktop) (версия 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (версия 1.29+)

**Установка и запуск:**

1. Клонируйте репозиторий:
```bash
git clone https://github.com/devmanorg/star-burger.git
cd star-burger
```

2. Подготовьте окружение:
```bash
cp .env.example .env
```

Отредактируйте файл `.env` и установите нужные значения (по крайней мере `SECRET_KEY` и `YANDEX_GEOCODE_API_KEY`):

```bash
SECRET_KEY=your-secret-key-here
YANDEX_GEOCODE_API_KEY=your-yandex-api-key
DEBUG=True
DB_NAME=starburger
DB_USER=starburger
DB_PASSWORD=starburger
```

3. Запустите приложение:
```bash
docker-compose up -d
```

Или используйте быстрый скрипт развертывания:
```bash
chmod +x deploy-local.sh
./deploy-local.sh
```

4. Дождитесь инициализации БД (первый запуск может занять 30-60 секунд):
```bash
docker-compose logs -f backend
```

5. Откройте сайт в браузере:
- **Фронтенд:** http://localhost:8000
- **Админка:** http://localhost:8000/admin (пользователь: admin, пароль: admin)

**Полезные команды:**

```bash
# Просмотр логов
docker-compose logs -f backend      # Логи бэкенда
docker-compose logs -f frontend     # Логи фронтенда
docker-compose logs -f db           # Логи БД

# Выполнение команд Django
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell

# Остановка приложения
docker-compose down

# Остановка и удаление данных
docker-compose down -v

# Пересборка образов (если изменились requirements)
docker-compose build --no-cache

# Просмотр статуса контейнеров
docker-compose ps
```

**Структура контейнеров:**

- **backend** (Django) — основное приложение, port 8000
- **frontend** (Node.js) — сборка фронтенда в режиме watch
- **db** (PostgreSQL) — база данных, port 5432

**Хранение данных:**

- **Медиа файлы:** хранятся в Docker volume `media_data`
- **База данных:** хранится в Docker volume `postgres_data`
- **Статические файлы:** хранятся в Docker volume `static_data`

Эти тома сохраняют данные даже после остановки и удаления контейнеров. Для полной очистки используйте `docker-compose down -v`.

---

### Локально без Docker (Для опытных разработчиков)

#### Как собрать бэкенд

Скачайте код:
```sh
git clone https://github.com/devmanorg/star-burger.git
```

Перейдите в каталог проекта:
```sh
cd star-burger
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.6.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии. 

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`


Установите зависимости в виртуальное окружение:
```sh
pip install -r backend/requirements.txt
```

Определите переменную окружения `SECRET_KEY`. Создать файл `.env` в каталоге проекта и положите туда такой код:
```sh
SECRET_KEY=django-insecure-0if40nf4nf93n4
YANDEX_GEOCODE_API_KEY=ваш-токен-яндекса
```

Если используете PostgreSQL, обновите переменные БД в `.env`:
```sh
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=starburger
DB_USER=starburger_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Создайте файл базы данных и отмигрируйте её следующей командой:

```sh
python backend/manage.py migrate
```

Запустите сервер:

```sh
python backend/manage.py runserver
```

Откройте сайт в браузере по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу, то не пугайтесь, выдохните. Просто фронтенд пока ещё не собран. Переходите к следующему разделу README.

#### Собрать фронтенд

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `runserver` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `runserver` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что Node.js и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```sh
nodejs --version
# v16.16.0
# Если ошибка, попробуйте node:
node --version
# v16.16.0

npm --version
# 8.11.0
```

Версия `nodejs` должна быть не младше `10.0` и не старше `16.16`. Лучше ставьте `16.16.0`, её мы тестировали. Версия `npm` не важна. Как обновить Node.js читайте в статье: [How to Update Node.js](https://phoenixnap.com/kb/update-node-js-version).

Перейдите в каталог проекта и установите пакеты Node.js:

```sh
cd star-burger
cd frontend
npm ci --dev
```

Команда `npm ci` создаст каталог `node_modules` и установит туда пакеты Node.js. Получится аналог виртуального окружения как для Python, но для Node.js.

Помимо прочего будет установлен [Parcel](https://parceljs.org/) — это упаковщик веб-приложений, похожий на [Webpack](https://webpack.js.org/). В отличии от Webpack он прост в использовании и совсем не требует настроек.

Теперь запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:

```sh
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Если вы на Windows, то вам нужна та же команда, только с другими слешами в путях:

```sh
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:

```
✨  Built in 10.89s
```

Parcel будет следить за файлами в каталоге `bundles-src`. Сначала он прочитает содержимое `index.js` и узнает какие другие файлы он импортирует. Затем Parcel перейдёт в каждый из этих подключенных файлов и узнает что импортируют они. И так далее, пока не закончатся файлы. В итоге Parcel получит полный список зависимостей. Дальше он соберёт все эти сотни мелких файлов в большие бандлы `bundles/index.js` и `bundles/index.css`. Они полностью самодостаточны, и потому пригодны для запуска в браузере. Именно эти бандлы сервер отправит клиенту.

Теперь если зайти на страницу  [http://127.0.0.1:8000/](http://127.0.0.1:8000/), то вместо пустой страницы вы увидите:

![](https://dvmn.org/filer/canonical/1594651900/687/)

Каталог `bundles` в репозитории особенный — туда Parcel складывает результаты своей работы. Эта директория предназначена исключительно для результатов сборки фронтенда и потому исключёна из репозитория с помощью `.gitignore`.

**Сбросьте кэш браузера <kbd>Ctrl-F5</kbd>.** Браузер при любой возможности старается кэшировать файлы статики: CSS, картинки и js-код. Порой это приводит к странному поведению сайта, когда код уже давно изменился, но браузер этого не замечает и продолжает использовать старую закэшированную версию. В норме Parcel решает эту проблему самостоятельно. Он следит за пересборкой фронтенда и предупреждает JS-код в браузере о необходимости подтянуть свежий код. Но если вдруг что-то у вас идёт не так, то начните ремонт со сброса браузерного кэша, жмите <kbd>Ctrl-F5</kbd>.

---

## Как развернуть на сервер (Production Deployment)

### Требования

- VPS/Dedicated Server с 2GB+ RAM
- Docker и Docker Compose установлены на сервере
- SSH доступ к серверу
- Доменное имя (опционально, для SSL)

### Подготовка сервера

1. Установите Docker и Docker Compose на сервер:

```bash
# SSH на сервер
ssh root@your.server.com

# Обновить систему
apt-get update && apt-get upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установить Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

2. Создайте директорию для проекта и клонируйте репозиторий:

```bash
mkdir -p /var/www/star-burger
cd /var/www/star-burger
git clone https://github.com/your-username/star-burger.git .
```

3. Подготовьте конфигурацию:

```bash
# Скопируйте пример конфига
cp .env.prod.example .env

# Отредактируйте с реальными значениями
nano .env
```

Важные переменные для production:
```bash
SECRET_KEY=change-me-to-real-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=starburger_prod
DB_USER=starburger_prod
DB_PASSWORD=very-secure-password
YANDEX_GEOCODE_API_KEY=your-api-key
ROLLBAR_ACCESS_TOKEN=optional
```

### Развертывание с помощью скрипта (Рекомендуется)

На локальной машине в каталоге проекта используйте скрипт деплоя:

```bash
chmod +x deploy.sh

# Синтаксис: ./deploy.sh <server_host> <server_user>
./deploy.sh your.server.com root
```

Скрипт автоматически:
- Обновит код с GitHub
- Пересоберет Docker образы
- Выполнит миграции БД
- Собере статические файлы
- Перезапустит контейнеры

### Развертывание вручную

Если скрипт не подходит, выполните на сервере:

```bash
cd /var/www/star-burger

# Обновить код
git pull origin main

# Пересобрать и запустить
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Выполнить миграции
sleep 5
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --noinput

# Собрать статические файлы
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput
```

### Конфигурация SSL (HTTPS)

Если используется Let's Encrypt:

```bash
# Установить certbot на сервер
apt-get install certbot python3-certbot-nginx

# Создать сертификат
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# В nginx.conf путь к сертификатам:
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

# Перезагрузить nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Мониторинг и поддержка

Просмотр логов:
```bash
# Все ошибки приложения
docker-compose -f docker-compose.prod.yml logs -f backend

# Nginx логи
docker-compose -f docker-compose.prod.yml logs -f nginx

# Все логи
docker-compose -f docker-compose.prod.yml logs -f
```

Проверка статуса приложения:
```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Health check
curl http://localhost/health
```

Очистка и переустановка:
```bash
# Удалить все контейнеры и том БД
docker-compose -f docker-compose.prod.yml down -v

# Переустановить с нуля
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate
```

---

## Структура Docker файлов

```
├── Dockerfile.backend        # Build для Django приложения
├── Dockerfile.frontend       # Build для Frontend (Node.js)
├── docker-compose.yml        # Dev конфигурация
├── docker-compose.prod.yml   # Production конфигурация
├── docker-entrypoint.sh      # Скрипт инициализации Django
├── .dockerignore             # Файлы исключенные из Docker образа
├── nginx.conf                # Nginx конфигурация для Production
├── deploy.sh                 # Скрипт автоматического деплоя на сервер
└── deploy-local.sh           # Скрипт быстрого локального деплоя
```

---

## 🚀 Быстрый деплой на сервер

```bash
cd /opt/StarBurger
./deploy_star_burger.sh
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
