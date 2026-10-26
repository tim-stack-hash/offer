"""Клавиатуры выбора и смены языка, запроса номера телефона."""

from __future__ import annotations

from telegram import KeyboardButton, ReplyKeyboardMarkup

from bot.content.texts import (
	CHANGE_LANGUAGE_BUTTONS,
	CONTACT_BUTTON_TEXT,
	FEEDBACK_CATEGORY_BUTTONS,
	LANGUAGE_BUTTONS,
	SUPPORT_CANCEL_BUTTONS,
)


def language_selection_keyboard() -> ReplyKeyboardMarkup:
	"""Клавиатура выбора языка интерфейса (показывается на старте и при смене языка)."""
	buttons = [KeyboardButton(label) for label, _ in LANGUAGE_BUTTONS]
	return ReplyKeyboardMarkup(
		[buttons[row_start:row_start + 2] for row_start in range(0, len(buttons), 2)],
		resize_keyboard=True,
		is_persistent=True,
	)


def contact_request_keyboard(language: str) -> ReplyKeyboardMarkup:
	"""Клавиатура с кнопкой запроса номера телефона и сменой языка."""
	button_text = CONTACT_BUTTON_TEXT.get(language, CONTACT_BUTTON_TEXT["ru"])
	return ReplyKeyboardMarkup(
		[
			[
				KeyboardButton(button_text, request_contact=True),
			],
			[KeyboardButton(CHANGE_LANGUAGE_BUTTONS.get(language, CHANGE_LANGUAGE_BUTTONS["ru"]))],
		],
		resize_keyboard=True,
		is_persistent=True,
	)


def change_language_keyboard(language: str) -> ReplyKeyboardMarkup:
	"""Клавиатура с единственной кнопкой смены языка."""
	return ReplyKeyboardMarkup(
		[[KeyboardButton(CHANGE_LANGUAGE_BUTTONS.get(language, CHANGE_LANGUAGE_BUTTONS["ru"]))]],
		resize_keyboard=True,
		is_persistent=True,
	)


def support_cancel_keyboard(language: str) -> ReplyKeyboardMarkup:
	"""Клавиатура отмены ввода обращения в поддержку."""
	return ReplyKeyboardMarkup(
		[[KeyboardButton(SUPPORT_CANCEL_BUTTONS.get(language, SUPPORT_CANCEL_BUTTONS["ru"]))]],
		resize_keyboard=True,
		is_persistent=True,
	)


def feedback_category_keyboard(language: str) -> ReplyKeyboardMarkup:
	"""Клавиатура выбора предложения или жалобы с кнопкой отмены."""
	buttons = FEEDBACK_CATEGORY_BUTTONS.get(
		language,
		FEEDBACK_CATEGORY_BUTTONS["ru"],
	)
	return ReplyKeyboardMarkup(
		[
			[KeyboardButton(button) for button in buttons],
			[KeyboardButton(SUPPORT_CANCEL_BUTTONS.get(language, SUPPORT_CANCEL_BUTTONS["ru"]))],
		],
		resize_keyboard=True,
		is_persistent=True,
	)
