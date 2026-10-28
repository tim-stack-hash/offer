#!/usr/bin/env bash
# Запуск бота на macOS / Linux. Настройки берутся из .env в корне проекта
# или из переменных окружения; при ошибке бот сам подскажет, чего не хватает.
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/python -m bot
