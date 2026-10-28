"""Инлайн-клавиатуры для выбора адвоката и работы с отзывами."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.content.lawyers import LAWYERS
from bot.content.lawyer_regions import LAWYER_REGIONS
from bot.content.texts import LAWYER_ACTION_BUTTONS, LAWYER_REVIEW_MENU_BUTTONS


def lawyer_regions_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Показывает регионы для адвокатов в двух колонках."""
	buttons = [
		InlineKeyboardButton(
			region_names.get(language, region_names["ru"]),
			callback_data=f"lawyer:region:{region_id}",
		)
		for region_id, region_names in LAWYER_REGIONS.items()
	]
	return InlineKeyboardMarkup(
		[
			buttons[row_start:row_start + 2]
			for row_start in range(0, len(buttons), 2)
		]
	)


def lawyers_by_region_keyboard(region_id: str) -> InlineKeyboardMarkup:
	"""Показывает адвокатов, зарегистрированных в выбранном регионе."""
	buttons = [
		InlineKeyboardButton(
			lawyer["name"],
			callback_data=f"lawyer:profile:{lawyer_id}",
		)
		for lawyer_id, lawyer in LAWYERS.items()
		if lawyer["region"] == region_id
	]
	return InlineKeyboardMarkup(
		[[button] for button in buttons]
	)


def lawyer_profile_keyboard(language: str, lawyer_id: str) -> InlineKeyboardMarkup:
	"""Кнопки перехода к отзывам и вызова выбранного адвоката."""
	reviews_text, call_text = LAWYER_ACTION_BUTTONS.get(
		language,
		LAWYER_ACTION_BUTTONS["ru"],
	)
	return InlineKeyboardMarkup(
		[
			[
				InlineKeyboardButton(
					reviews_text,
					callback_data=f"lawyer:reviews:{lawyer_id}",
				)
			],
			[
				InlineKeyboardButton(
					call_text,
					callback_data=f"lawyer:call:{lawyer_id}",
				)
			],
		]
	)


def lawyer_review_menu_keyboard(language: str, lawyer_id: str) -> InlineKeyboardMarkup:
	"""Кнопки создания или просмотра отзывов об адвокате."""
	write_text, read_text = LAWYER_REVIEW_MENU_BUTTONS.get(
		language,
		LAWYER_REVIEW_MENU_BUTTONS["ru"],
	)
	return InlineKeyboardMarkup(
		[
			[
				InlineKeyboardButton(
					write_text,
					callback_data=f"lawyer:write_review:{lawyer_id}",
				)
			],
			[
				InlineKeyboardButton(
					read_text,
					callback_data=f"lawyer:show_reviews:{lawyer_id}",
				)
			],
		]
	)
