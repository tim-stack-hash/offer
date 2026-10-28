"""Единая точка подключения к SQLite."""

from __future__ import annotations

import logging
import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager

from bot.config import DEFAULT_DATABASE_PATH, LEGACY_USER_DATABASE_PATH, get_database_path

LOGGER = logging.getLogger(__name__)

# Сколько секунд ждать, если базу в этот момент пишет другой процесс (бот или веб-панель).
BUSY_TIMEOUT_SECONDS = 30


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
	"""Открывает соединение и гарантированно закрывает его после использования."""
	with closing(sqlite3.connect(get_database_path(), timeout=BUSY_TIMEOUT_SECONDS)) as connection:
		yield connection


def prepare_database_file() -> None:
	"""Создаёт каталог базы, переносит базу из старого расположения и включает WAL."""
	database_path = get_database_path()
	os.makedirs(os.path.dirname(database_path) or ".", exist_ok=True)
	# Переносим только в расположение по умолчанию: если путь задан явно (например,
	# во время тестов), рабочую базу трогать нельзя.
	if (
		database_path == DEFAULT_DATABASE_PATH
		and not os.path.exists(database_path)
		and os.path.exists(LEGACY_USER_DATABASE_PATH)
	):
		os.replace(LEGACY_USER_DATABASE_PATH, database_path)
		LOGGER.info("Moved database %s -> %s", LEGACY_USER_DATABASE_PATH, database_path)

	with connect() as connection:
		# WAL позволяет веб-панели читать базу, пока бот в неё пишет.
		connection.execute("PRAGMA journal_mode=WAL")
