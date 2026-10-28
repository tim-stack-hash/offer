"""Настройки из переменных окружения (.env) с проверкой значений."""

from __future__ import annotations

import os
from functools import lru_cache

from bot.config.constants import (
	DEFAULT_FEEDBACK_CHAT_ID,
	DEFAULT_LAWYER_REVIEWS_CHAT_ID,
	DEFAULT_SUPPORT_CHAT_ID,
)
from bot.config.paths import DEFAULT_DATABASE_PATH, DEFAULT_PERSISTENCE_PATH

TELEGRAM_BOT_TOKEN_ENV = "TELEGRAM_BOT_TOKEN"
ADMIN_USER_IDS_ENV = "ADMIN_USER_IDS"
LAWYER_REVIEWS_CHAT_ID_ENV = "LAWYER_REVIEWS_CHAT_ID"
SUPPORT_CHAT_ID_ENV = "SUPPORT_CHAT_ID"
FEEDBACK_CHAT_ID_ENV = "FEEDBACK_CHAT_ID"
DATABASE_PATH_ENV = "DATABASE_PATH"
PERSISTENCE_PATH_ENV = "PERSISTENCE_PATH"
PROTECT_CONTENT_ENV = "PROTECT_CONTENT"
LOG_LEVEL_ENV = "LOG_LEVEL"


def get_bot_token() -> str:
	"""Возвращает токен бота или сообщает, что он не задан."""
	token = os.getenv(TELEGRAM_BOT_TOKEN_ENV, "").strip()
	if not token:
		raise RuntimeError(f"Set the {TELEGRAM_BOT_TOKEN_ENV} environment variable")
	return token


@lru_cache(maxsize=None)
def _parse_admin_user_ids(raw_admin_ids: str) -> frozenset[int]:
	if not raw_admin_ids:
		raise RuntimeError(
			f"Set {ADMIN_USER_IDS_ENV} to the Telegram ID of at least one bot administrator"
		)

	try:
		admin_ids = [int(value.strip()) for value in raw_admin_ids.split(",") if value.strip()]
	except ValueError as error:
		raise RuntimeError(
			f"{ADMIN_USER_IDS_ENV} must contain comma-separated numeric Telegram IDs"
		) from error

	if not admin_ids or any(admin_id <= 0 for admin_id in admin_ids):
		raise RuntimeError(f"{ADMIN_USER_IDS_ENV} must contain positive Telegram IDs")
	return frozenset(admin_ids)


def parse_admin_user_ids() -> frozenset[int]:
	"""Читает и проверяет список Telegram ID администраторов из переменной окружения."""
	return _parse_admin_user_ids(os.getenv(ADMIN_USER_IDS_ENV, "").strip())


def is_admin(user_id: int) -> bool:
	"""Проверяет, входит ли указанный Telegram ID в список администраторов."""
	return user_id in parse_admin_user_ids()


def _chat_id_from_env(env_name: str, default: int) -> int:
	raw_chat_id = os.getenv(env_name, "").strip() or str(default)
	try:
		return int(raw_chat_id)
	except ValueError as error:
		raise RuntimeError(f"{env_name} must be a numeric Telegram chat ID") from error


def get_lawyer_reviews_chat_id() -> int:
	"""ID канала, куда публикуются отзывы об адвокатах."""
	return _chat_id_from_env(LAWYER_REVIEWS_CHAT_ID_ENV, DEFAULT_LAWYER_REVIEWS_CHAT_ID)


def get_support_chat_id() -> int:
	"""ID группы, куда пересылаются обращения в поддержку."""
	return _chat_id_from_env(SUPPORT_CHAT_ID_ENV, DEFAULT_SUPPORT_CHAT_ID)


def get_feedback_chat_id() -> int:
	"""ID группы, куда отправляются предложения и жалобы."""
	return _chat_id_from_env(FEEDBACK_CHAT_ID_ENV, DEFAULT_FEEDBACK_CHAT_ID)


def get_database_path() -> str:
	"""Путь к файлу SQLite (по умолчанию data/bot_users.sqlite3)."""
	return os.getenv(DATABASE_PATH_ENV, "").strip() or DEFAULT_DATABASE_PATH


def get_persistence_path() -> str:
	"""Путь к файлу, где хранится состояние пользователей и диалогов между перезапусками."""
	return os.getenv(PERSISTENCE_PATH_ENV, "").strip() or DEFAULT_PERSISTENCE_PATH


def is_content_protected() -> bool:
	"""Запрещать ли пересылку и сохранение сообщений бота."""
	return os.getenv(PROTECT_CONTENT_ENV, "").strip().lower() in ("1", "true", "yes", "on")


def get_log_level() -> str:
	return os.getenv(LOG_LEVEL_ENV, "INFO").strip().upper() or "INFO"


def validate_settings() -> None:
	"""Проверяет все обязательные настройки при старте, чтобы бот не упал позже."""
	get_bot_token()
	parse_admin_user_ids()
	get_lawyer_reviews_chat_id()
	get_support_chat_id()
	get_feedback_chat_id()
