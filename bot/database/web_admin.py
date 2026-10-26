"""Read-only queries used by the web administrator dashboard."""

from __future__ import annotations

import sqlite3
from contextlib import closing

from bot.config import USER_DATABASE_PATH
from bot.database.activity import format_click_time


def get_web_dashboard_summary() -> dict[str, int]:
	"""Returns totals for users and recorded button clicks."""
	with closing(sqlite3.connect(USER_DATABASE_PATH)) as connection:
		users_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
		active_users, clicks_count = connection.execute(
			"""
			SELECT COUNT(DISTINCT user_id), COALESCE(SUM(click_count), 0)
			FROM user_action_counts
			"""
		).fetchone()
	return {
		"users_count": users_count,
		"active_users": active_users,
		"clicks_count": clicks_count,
	}


def get_web_activity_counts() -> list[dict[str, int | str]]:
	"""Returns global counts and latest click time for every recorded button."""
	with closing(sqlite3.connect(USER_DATABASE_PATH)) as connection:
		rows = connection.execute(
			"""
			SELECT
				action,
				SUM(click_count) AS clicks,
				COUNT(DISTINCT user_id) AS users,
				MAX(last_clicked_at) AS last_clicked_at
			FROM user_action_counts
			GROUP BY action
			ORDER BY clicks DESC, action
			"""
		).fetchall()
	return [
		{
			"action": action,
			"clicks": clicks,
			"users": users,
			"last_clicked_at": format_click_time(last_clicked_at),
		}
		for action, clicks, users, last_clicked_at in rows
	]


def get_web_users(
	search: str,
	limit: int,
	offset: int,
) -> tuple[int, list[dict[str, int | str]]]:
	"""Returns a filtered, paginated user list and its total result count."""
	search_pattern = f"%{search}%"
	search_filter = """
		(? = '' OR CAST(users.user_id AS TEXT) LIKE ?
			OR COALESCE(users.first_name, '') LIKE ?
			OR COALESCE(users.last_name, '') LIKE ?
			OR COALESCE(users.username, '') LIKE ?
			OR COALESCE(users.phone_number, '') LIKE ?)
	"""
	parameters = (search, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern)
	with closing(sqlite3.connect(USER_DATABASE_PATH)) as connection:
		total = connection.execute(
			f"SELECT COUNT(*) FROM users WHERE {search_filter}",
			parameters,
		).fetchone()[0]
		rows = connection.execute(
			f"""
			SELECT
				users.user_id,
				users.first_name,
				users.last_name,
				users.username,
				users.phone_number,
				COALESCE(activity.click_count, 0),
				activity.last_clicked_at
			FROM users
			LEFT JOIN (
				SELECT user_id, SUM(click_count) AS click_count, MAX(last_clicked_at) AS last_clicked_at
				FROM user_action_counts
				GROUP BY user_id
			) AS activity ON activity.user_id = users.user_id
			WHERE {search_filter}
			ORDER BY users.first_name COLLATE NOCASE, users.last_name COLLATE NOCASE, users.user_id
			LIMIT ? OFFSET ?
			""",
			(*parameters, limit, offset),
		).fetchall()
	return total, [
		{
			"user_id": user_id,
			"first_name": first_name,
			"last_name": last_name,
			"username": username or "",
			"phone_number": phone_number or "",
			"click_count": click_count,
			"last_clicked_at": format_click_time(last_clicked_at),
		}
		for (
			user_id,
			first_name,
			last_name,
			username,
			phone_number,
			click_count,
			last_clicked_at,
		) in rows
	]


def get_web_click_history(
	search: str,
	limit: int,
	offset: int,
) -> tuple[int, list[dict[str, int | str]]]:
	"""Returns filtered, paginated individual button click events."""
	search_pattern = f"%{search}%"
	search_filter = """
		(? = '' OR CAST(users.user_id AS TEXT) LIKE ?
			OR COALESCE(users.first_name, '') LIKE ?
			OR COALESCE(users.last_name, '') LIKE ?
			OR COALESCE(users.username, '') LIKE ?
			OR COALESCE(users.phone_number, '') LIKE ?
			OR user_action_events.action LIKE ?)
	"""
	parameters = (
		search,
		search_pattern,
		search_pattern,
		search_pattern,
		search_pattern,
		search_pattern,
		search_pattern,
	)
	with closing(sqlite3.connect(USER_DATABASE_PATH)) as connection:
		total = connection.execute(
			f"""
			SELECT COUNT(*)
			FROM user_action_events
			JOIN users ON users.user_id = user_action_events.user_id
			WHERE {search_filter}
			""",
			parameters,
		).fetchone()[0]
		rows = connection.execute(
			f"""
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
			WHERE {search_filter}
			ORDER BY user_action_events.clicked_at DESC, user_action_events.id DESC
			LIMIT ? OFFSET ?
			""",
			(*parameters, limit, offset),
		).fetchall()
	return total, [
		{
			"user_id": user_id,
			"name": " ".join(part for part in (first_name, last_name) if part),
			"username": username or "",
			"phone_number": phone_number or "",
			"action": action,
			"clicked_at": format_click_time(clicked_at),
		}
		for user_id, first_name, last_name, username, phone_number, action, clicked_at in rows
	]
