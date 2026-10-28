"""Общие помощники обработчиков: язык пользователя, текущая клавиатура, длина текста."""

from __future__ import annotations

from telegram import ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from bot.config import DEFAULT_LANGUAGE
from bot.content.colonies import COLONY_GROUPS
from bot.keyboards import (
	change_language_keyboard,
	colony_location_reply_keyboard,
	language_selection_keyboard,
)


def user_language(context: ContextTypes.DEFAULT_TYPE) -> str:
	"""Язык интерфейса текущего пользователя."""
	return context.user_data.get("language") or DEFAULT_LANGUAGE


def telegram_text_length(text: str) -> int:
	"""Длина текста так, как её считает Telegram (в UTF-16)."""
	return len(text.encode("utf-16-le")) // 2


def full_name(first_name: str | None, last_name: str | None) -> str:
	return " ".join(part for part in (first_name, last_name) if part)


def return_user_keyboard(context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
	"""Клавиатура, соответствующая текущему шагу пользователя."""
	if not context.user_data.get("language"):
		return language_selection_keyboard()

	language = user_language(context)
	colony = context.user_data.get("colony")
	if colony in COLONY_GROUPS:
		keyboard = colony_location_reply_keyboard(
			language, colony, context.user_data.get("menu_section", "root")
		)
		if keyboard:
			return keyboard
	return change_language_keyboard(language)
