"""Счётчики нажатий пользовательских кнопок и их выгрузка."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from bot.config import LOCAL_TIMEZONE
from bot.database.connection import connect
from bot.database.users import csv_safe_cell

RUSSIAN_MONTHS = (
	"января",
	"февраля",
	"марта",
	"апреля",
	"мая",
	"июня",
	"июля",
	"августа",
	"сентября",
	"октября",
	"ноября",
	"декабря",
)


def format_click_time(timestamp: str | None) -> str:
	"""Показывает время нажатия в часовом поясе UTC+05:00."""
	if not timestamp:
		return ""

	clicked_at = datetime.fromisoformat(timestamp)
	if clicked_at.tzinfo is None:
		clicked_at = clicked_at.replace(tzinfo=timezone.utc)
	local_time = clicked_at.astimezone(LOCAL_TIMEZONE)
	return (
		f"{local_time.day} {RUSSIAN_MONTHS[local_time.month - 1]} "
		f"{local_time.year} года, {local_time:%H:%M:%S} (UTC+05:00)"
	)


def record_user_action(user_id: int, action: str) -> int:
	"""Сохраняет нажатие и возвращает общее число действий пользователя."""
	clicked_at = datetime.now(LOCAL_TIMEZONE).isoformat(timespec="seconds")
	with connect() as connection:
		with connection:
			connection.execute(
				"""
				INSERT INTO user_action_counts (user_id, action, click_count, last_clicked_at)
				VALUES (?, ?, 1, ?)
				ON CONFLICT(user_id, action) DO UPDATE SET
					click_count = click_count + 1,
					last_clicked_at = excluded.last_clicked_at
				""",
				(user_id, action, clicked_at),
			)
			connection.execute(
				"""
				INSERT INTO user_action_events (user_id, action, clicked_at)
				VALUES (?, ?, ?)
				""",
				(user_id, action, clicked_at),
			)
			return connection.execute(
				"""
				SELECT COALESCE(SUM(click_count), 0)
				FROM user_action_counts
				WHERE user_id = ?
				""",
				(user_id,),
			).fetchone()[0]


def get_activity_summary() -> tuple[int, int, list[tuple[str, int]]]:
	"""Возвращает число отслеживаемых пользователей, кликов и популярные кнопки."""
	with connect() as connection:
		with connection:
			users_count, clicks_count = connection.execute(
				"""
				SELECT COUNT(DISTINCT user_id), COALESCE(SUM(click_count), 0)
				FROM user_action_counts
				"""
			).fetchone()
			top_actions = connection.execute(
				"""
				SELECT action, SUM(click_count) AS total_clicks
				FROM user_action_counts
				GROUP BY action
				ORDER BY total_clicks DESC, action
				LIMIT 10
				"""
			).fetchall()
	return users_count, clicks_count, top_actions


def export_user_activity_csv() -> io.BytesIO:
	"""Формирует сводный CSV со счётчиком и временем последнего нажатия каждой кнопки."""
	with connect() as connection:
		with connection:
			rows = connection.execute(
				"""
				SELECT
					users.user_id,
					users.first_name,
					users.last_name,
					users.username,
					users.phone_number,
					user_action_counts.action,
					COALESCE(user_action_counts.click_count, 0),
					user_action_counts.last_clicked_at
				FROM users
				LEFT JOIN user_action_counts ON users.user_id = user_action_counts.user_id
				ORDER BY users.first_name, users.last_name, user_action_counts.action
				"""
			).fetchall()

	csv_text = io.StringIO(newline="")
	writer = csv.writer(csv_text)
	writer.writerow((
		"Telegram ID",
		"Имя",
		"Фамилия",
		"Username",
		"Телефон",
		"Кнопка / действие",
		"Количество нажатий",
		"Последнее нажатие (UTC+05:00)",
	))
	for user_id, first_name, last_name, username, phone, action, count, last_clicked_at in rows:
		writer.writerow((
			user_id,
			csv_safe_cell(first_name),
			csv_safe_cell(last_name),
			csv_safe_cell(username),
			csv_safe_cell(phone),
			csv_safe_cell(action),
			count,
			format_click_time(last_clicked_at),
		))

	return io.BytesIO(csv_text.getvalue().encode("utf-8-sig"))


def export_user_activity_history_csv() -> io.BytesIO:
	"""Формирует CSV с отдельной строкой для каждого нажатия пользователем кнопки."""
	with connect() as connection:
		with connection:
			rows = connection.execute(
				"""
				SELECT
					users.user_id,
					users.first_name,
					users.last_name,
					users.username,
					users.phone_number,
					user_action_events.action,
					user_action_events.clicked_at
				FROM user_action_events
				JOIN users ON users.user_id = user_action_events.user_id
				ORDER BY user_action_events.clicked_at DESC, user_action_events.id DESC
				"""
			).fetchall()

	csv_text = io.StringIO(newline="")
	writer = csv.writer(csv_text)
	writer.writerow((
		"Telegram ID",
		"Имя",
		"Фамилия",
		"Username",
		"Телефон",
		"Кнопка / действие",
		"Дата и время нажатия (UTC+05:00)",
	))
	for user_id, first_name, last_name, username, phone, action, clicked_at in rows:
		writer.writerow((
			user_id,
			csv_safe_cell(first_name),
			csv_safe_cell(last_name),
			csv_safe_cell(username),
			csv_safe_cell(phone),
			csv_safe_cell(action),
			format_click_time(clicked_at),
		))

	return io.BytesIO(csv_text.getvalue().encode("utf-8-sig"))
