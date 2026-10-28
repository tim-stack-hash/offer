from __future__ import annotations

from bot.database import (
	csv_safe_cell,
	export_users_csv,
	get_support_message_recipient,
	get_user_count,
	get_user_language,
	get_user_phone_number,
	record_user_action,
	register_support_message,
	register_user,
	save_lawyer_review,
	get_lawyer_reviews,
	save_user_language,
	save_user_phone_number,
)


def test_register_user_reports_only_first_registration():
	assert register_user(5, "nick", "Ivan", None) is True
	assert register_user(5, "nick2", "Ivan", "Petrov") is False
	assert get_user_count() == 1


def test_language_and_phone_round_trip():
	register_user(5, None, "Ivan", None)
	save_user_language(5, "uz")
	save_user_phone_number(5, "+998901234567")
	assert get_user_language(5) == "uz"
	assert get_user_phone_number(5) == "+998901234567"
	assert get_user_language(404) is None


def test_action_counter_accumulates():
	assert record_user_action(7, "a") == 1
	assert record_user_action(7, "b") == 2
	assert record_user_action(7, "a") == 3


def test_support_message_mapping():
	register_support_message(-100, 42, 7)
	assert get_support_message_recipient(-100, 42) == 7
	assert get_support_message_recipient(-100, 43) is None


def test_lawyer_reviews_include_author():
	register_user(8, "author", "Anna", None)
	save_lawyer_review("tima", 8, "Хороший адвокат")
	(review, _created_at, author), = get_lawyer_reviews("tima")
	assert review == "Хороший адвокат"
	assert author == "Anna (@author)"


def test_csv_export_escapes_formulas():
	register_user(9, None, "=HYPERLINK()", None)
	assert csv_safe_cell("=1+1") == "'=1+1"
	assert "'=HYPERLINK()" in export_users_csv().getvalue().decode("utf-8-sig")
