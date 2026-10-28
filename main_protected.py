"""Устаревшая точка входа: то же, что main.py с PROTECT_CONTENT=true.

Оставлена для совместимости со старыми скриптами запуска; используйте
PROTECT_CONTENT=true в .env и main.py.
"""

import os

from bot.app import run

if __name__ == "__main__":
	os.environ["PROTECT_CONTENT"] = "true"
	run()
