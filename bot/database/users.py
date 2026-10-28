"""CRUD-операции над таблицей пользователей и выгрузка списка пользователей в CSV."""

from __future__ import annotations

import csv
import io

from bot.database.connection import connect, prepare_database_file


def initialize_user_database() -> None:
	"""Создаёт таблицу users при первом запуске и добавляет недостающие колонки при обновлении схемы."""
	prepare_database_file()
	with connect() as connection:
		with connection:
			connection.execute(
				"""
				CREATE TABLE IF NOT EXISTS users (
					user_id INTEGER PRIMARY KEY,
					username TEXT,
					first_name TEXT NOT NULL DEFAULT '',
					last_name TEXT NOT NULL DEFAULT '',
					phone_number TEXT,
					language TEXT NOT NULL DEFAULT 'ru'
				)
				"""
			)
			connection.execute(
				"""
				CREATE TABLE IF NOT EXISTS user_action_counts (
					user_id INTEGER NOT NULL,
					action TEXT NOT NULL,
					click_count INTEGER NOT NULL DEFAULT 0,
					last_clicked_at TEXT NOT NULL,
					PRIMARY KEY (user_id, action)
				)
				"""
			)
			connection.execute(
				"""
				CREATE TABLE IF NOT EXISTS user_action_events (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					user_id INTEGER NOT NULL,
					action TEXT NOT NULL,
					clicked_at TEXT NOT NULL
				)
				"""
			)
			connection.execute(
				"""
				CREATE INDEX IF NOT EXISTS user_action_events_by_user_time
				ON user_action_events (user_id, clicked_at)
				"""
			)
			connection.execute(
				"""
				CREATE INDEX IF NOT EXISTS user_action_events_by_time
				ON user_action_events (clicked_at, id)
				"""
			)
			connection.execute(
				"""
				CREATE TABLE IF NOT EXISTS lawyer_reviews (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					lawyer_id TEXT NOT NULL,
					user_id INTEGER NOT NULL,
					review TEXT NOT NULL,
					created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
				)
				"""
			)
			connection.execute(
				"""
				CREATE TABLE IF NOT EXISTS bot_media_files (
					media_key TEXT PRIMARY KEY,
					file_size INTEGER NOT NULL,
					file_id TEXT NOT NULL
				)
				"""
			)
			connection.execute(
				"""
				CREATE TABLE IF NOT EXISTS support_message_recipients (
					support_chat_id INTEGER NOT NULL,
					support_message_id INTEGER NOT NULL,
					user_id INTEGER NOT NULL,
					PRIMARY KEY (support_chat_id, support_message_id)
				)
				"""
			)
			connection.execute(
				"""
				CREATE INDEX IF NOT EXISTS lawyer_reviews_by_lawyer
				ON lawyer_reviews (lawyer_id, id)
				"""
			)
			existing_columns = {
				row[1] for row in connection.execute("PRAGMA table_info(users)")
			}
			for column_name, column_type in (
				("username", "TEXT"),
				("first_name", "TEXT NOT NULL DEFAULT ''"),
				("last_name", "TEXT NOT NULL DEFAULT ''"),
				("phone_number", "TEXT"),
				("language", "TEXT NOT NULL DEFAULT 'ru'"),
			):
				if column_name not in existing_columns:
					connection.execute(
						f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
					)


def register_user(
	user_id: int,
	username: str | None,
	first_name: str,
	last_name: str | None,
) -> bool:
	"""Добавляет нового пользователя (или обновляет его данные) и возвращает True, если пользователь новый."""
	with connect() as connection:
		with connection:
			cursor = connection.execute(
				"""
				INSERT OR IGNORE INTO users (
					user_id, username, first_name, last_name
				) VALUES (?, ?, ?, ?)
				""",
				(user_id, username, first_name, last_name or ""),
			)
			connection.execute(
				"""
				UPDATE users
				SET username = ?, first_name = ?, last_name = ?
				WHERE user_id = ?
				""",
				(username, first_name, last_name or "", user_id),
			)
			return cursor.rowcount > 0


def save_user_phone_number(user_id: int, phone_number: str) -> None:
	"""Сохраняет номер телефона, присланный пользователем, в базе."""
	with connect() as connection:
		with connection:
			connection.execute(
				"""
				INSERT INTO users (user_id, phone_number)
				VALUES (?, ?)
				ON CONFLICT(user_id) DO UPDATE SET phone_number = excluded.phone_number
				""",
				(user_id, phone_number),
			)


def get_user_phone_number(user_id: int) -> str | None:
	"""Возвращает сохранённый номер телефона пользователя, если он есть."""
	with connect() as connection:
		with connection:
			row = connection.execute(
				"SELECT phone_number FROM users WHERE user_id = ?",
				(user_id,),
			).fetchone()
	return row[0] if row else None


def get_user_language(user_id: int) -> str | None:
	"""Возвращает сохранённый язык интерфейса пользователя, если он есть."""
	with connect() as connection:
		with connection:
			row = connection.execute(
				"SELECT language FROM users WHERE user_id = ?",
				(user_id,),
			).fetchone()
	return row[0] if row else None


def save_user_language(user_id: int, language: str) -> None:
	"""Сохраняет выбранный пользователем язык интерфейса."""
	with connect() as connection:
		with connection:
			connection.execute(
				"""
				INSERT INTO users (user_id, language)
				VALUES (?, ?)
				ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
				""",
				(user_id, language),
			)


def get_registered_users() -> list[tuple[int, str]]:
	"""Возвращает Telegram ID и язык всех зарегистрированных пользователей."""
	with connect() as connection:
		with connection:
			rows = connection.execute(
				"SELECT user_id, language FROM users ORDER BY user_id"
			).fetchall()
	return [(user_id, language) for user_id, language in rows]


def get_cached_media_file_id(media_key: str, file_size: int) -> str | None:
	"""Возвращает сохранённый Telegram file_id, если исходный файл не менялся."""
	with connect() as connection:
		with connection:
			row = connection.execute(
				"""
				SELECT file_id, file_size
				FROM bot_media_files
				WHERE media_key = ?
				""",
				(media_key,),
			).fetchone()
	return row[0] if row and row[1] == file_size else None


def save_cached_media_file_id(
	media_key: str,
	file_size: int,
	file_id: str,
) -> None:
	"""Сохраняет Telegram file_id, чтобы повторно не загружать файл."""
	with connect() as connection:
		with connection:
			connection.execute(
				"""
				INSERT INTO bot_media_files (media_key, file_size, file_id)
				VALUES (?, ?, ?)
				ON CONFLICT(media_key) DO UPDATE SET
					file_size = excluded.file_size,
					file_id = excluded.file_id
				""",
				(media_key, file_size, file_id),
			)


def delete_cached_media_file_id(media_key: str) -> None:
	"""Удаляет недействительный Telegram file_id."""
	with connect() as connection:
		with connection:
			connection.execute(
				"DELETE FROM bot_media_files WHERE media_key = ?",
				(media_key,),
			)


def get_user_count() -> int:
	"""Возвращает общее количество зарегистрированных пользователей."""
	with connect() as connection:
		with connection:
			return connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def csv_safe_cell(value: str | None) -> str:
	"""Экранирует значение для CSV, чтобы Excel/Sheets не воспринял его как формулу."""
	text = value or ""
	if text.lstrip().startswith(("=", "+", "-", "@")):
		return f"'{text}"
	return text


def export_users_csv() -> io.BytesIO:
	"""Формирует CSV-файл со всеми пользователями (ID, username, имя, фамилия, телефон)."""
	with connect() as connection:
		with connection:
			users = connection.execute(
				"""
				SELECT user_id, username, first_name, last_name, phone_number
				FROM users
				ORDER BY user_id
				"""
			).fetchall()

	csv_text = io.StringIO(newline="")
	writer = csv.writer(csv_text)
	writer.writerow(("Telegram ID", "Username", "First name", "Last name", "Phone number"))
	for user_id, username, first_name, last_name, phone_number in users:
		writer.writerow((
			user_id,
			csv_safe_cell(username),
			csv_safe_cell(first_name),
			csv_safe_cell(last_name),
			csv_safe_cell(phone_number),
		))

	return io.BytesIO(csv_text.getvalue().encode("utf-8-sig"))
