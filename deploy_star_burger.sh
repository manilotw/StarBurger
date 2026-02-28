#!/usr/bin/env bash
set -e  # ❗ падать при любой ошибке

echo "🚀 Starting deploy..."

PROJECT_DIR="/opt/StarBurger"
VENV="$PROJECT_DIR/venv"

cd "$PROJECT_DIR"

echo "📦 Pull latest code"
git pull origin main

echo "🐍 Activate virtualenv"
source "$VENV/bin/activate"

echo "📦 Install Python dependencies"
pip install --no-cache-dir -r backend/requirements.txt

echo "🧱 Apply Django migrations"
python backend/manage.py migrate --noinput

echo "🎨 Collect Django static"
python backend/manage.py collectstatic --noinput

if [ -f frontend/package.json ]; then
  echo "📦 Install Node.js dependencies"
  cd frontend
  npm install

  echo "🛠 Build frontend"
  npm run build || echo "⚠️ No build script, skipping"
  cd "$PROJECT_DIR"
fi

echo "🔄 Restart Gunicorn & Nginx"
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "📡 Notify Rollbar about deploy"

set -a
source .env
set +a

ENVIRONMENT="production"
REVISION=$(git rev-parse HEAD)

curl -s https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_ACCESS_TOKEN \
  -F environment=$ENVIRONMENT \
  -F revision=$REVISION

echo "✅ Rollbar notified: $REVISION"
echo "✅ Deploy finished successfully!"

