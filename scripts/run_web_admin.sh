#!/usr/bin/env bash
# Запуск веб-панели администратора на 127.0.0.1:$WEB_ADMIN_PORT (по умолчанию 8080).
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/python -m bot.web
