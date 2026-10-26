#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then
	set -a
	source .env
	set +a
fi

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
	echo "Please set TELEGRAM_BOT_TOKEN before running the bot."
	echo 'Example: export TELEGRAM_BOT_TOKEN="123:ABC"'
	exit 1
fi

if [ -z "${ADMIN_USER_IDS:-}" ]; then
	echo "Please set ADMIN_USER_IDS to your numeric Telegram user ID before running the bot."
	echo 'Example: export ADMIN_USER_IDS="6048622285"'
	echo 'Multiple administrators: export ADMIN_USER_IDS="123456789,987654321"'
	exit 1
fi

"$(dirname "$0")/.venv/bin/python" "$(dirname "$0")/main.py"
