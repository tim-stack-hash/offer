"""Хранение связи между обращением в поддержку и пользователем."""

from __future__ import annotations


from bot.database.connection import connect


def register_support_message(
	support_chat_id: int,
	support_message_id: int,
	user_id: int,
) -> None:
	"""Сохраняет пользователя, которому принадлежит сообщение-обращение."""
	with connect() as connection:
		with connection:
			connection.execute(
				"""
				INSERT INTO support_message_recipients (
					support_chat_id, support_message_id, user_id
				)
				VALUES (?, ?, ?)
				ON CONFLICT(support_chat_id, support_message_id)
				DO UPDATE SET user_id = excluded.user_id
				""",
				(support_chat_id, support_message_id, user_id),
			)


def get_support_message_recipient(
	support_chat_id: int,
	support_message_id: int,
) -> int | None:
	"""Возвращает Telegram ID пользователя для сообщения-обращения."""
	with connect() as connection:
		with connection:
			row = connection.execute(
				"""
				SELECT user_id
				FROM support_message_recipients
				WHERE support_chat_id = ? AND support_message_id = ?
				""",
				(support_chat_id, support_message_id),
			).fetchone()
	return row[0] if row else None
