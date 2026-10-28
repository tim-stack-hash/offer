"""Сохранение и чтение отзывов об адвокатах."""

from __future__ import annotations


from bot.database.connection import connect


def save_lawyer_review(
	lawyer_id: str,
	user_id: int,
	review: str,
) -> tuple[int, str]:
	"""Сохраняет отзыв и возвращает его ID и время создания."""
	with connect() as connection:
		with connection:
			cursor = connection.execute(
				"""
				INSERT INTO lawyer_reviews (lawyer_id, user_id, review)
				VALUES (?, ?, ?)
				""",
				(lawyer_id, user_id, review),
			)
			review_id = cursor.lastrowid
			if review_id is None:
				raise RuntimeError("SQLite did not return an ID for the saved lawyer review")
			created_at = connection.execute(
				"SELECT created_at FROM lawyer_reviews WHERE id = ?",
				(review_id,),
			).fetchone()[0]
	return review_id, created_at


def get_lawyer_reviews(lawyer_id: str) -> list[tuple[str, str, str]]:
	"""Возвращает отзывы адвоката с именами авторов в порядке публикации."""
	with connect() as connection:
		with connection:
			rows = connection.execute(
				"""
				SELECT
					lawyer_reviews.review,
					lawyer_reviews.created_at,
					lawyer_reviews.user_id,
					users.first_name,
					users.last_name,
					users.username
				FROM lawyer_reviews
				LEFT JOIN users ON users.user_id = lawyer_reviews.user_id
				WHERE lawyer_reviews.lawyer_id = ?
				ORDER BY lawyer_reviews.id
				""",
				(lawyer_id,),
			).fetchall()

	reviews = []
	for review, created_at, user_id, first_name, last_name, username in rows:
		name = " ".join(part for part in (first_name or "", last_name or "") if part)
		if name and username:
			author = f"{name} (@{username})"
		elif name:
			author = name
		elif username:
			author = f"@{username}"
		else:
			author = f"ID {user_id}"
		reviews.append((review, created_at, author))
	return reviews


def get_lawyer_review_count(lawyer_id: str) -> int:
	"""Возвращает количество отзывов об адвокате."""
	with connect() as connection:
		with connection:
			return connection.execute(
				"SELECT COUNT(*) FROM lawyer_reviews WHERE lawyer_id = ?",
				(lawyer_id,),
			).fetchone()[0]
