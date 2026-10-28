"""Общие помощники обработчиков: язык пользователя, оформление сообщений, экраны меню."""

from __future__ import annotations

import html

from telegram import ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.config import DEFAULT_LANGUAGE
from bot.content.colonies import COLONY_GROUP_LABELS, COLONY_GROUPS
from bot.content.texts import MENU_SECTION_TEXTS, NO_DATA_TEXTS, STEP_LABELS
from bot.keyboards import (
	MENU_SECTION_BUTTONS,
	change_language_keyboard,
	colony_location_reply_keyboard,
	language_selection_keyboard,
)

# Сообщения с <b>…</b> отправляются с этим режимом разметки; всё подставляемое
# в них экранируется функцией escape, иначе Telegram отклонит сообщение.
HTML = ParseMode.HTML


def user_language(context: ContextTypes.DEFAULT_TYPE) -> str:
	"""Язык интерфейса текущего пользователя."""
	return context.user_data.get("language") or DEFAULT_LANGUAGE


def telegram_text_length(text: str) -> int:
	"""Длина текста так, как её считает Telegram (в UTF-16)."""
	return len(text.encode("utf-16-le")) // 2


def full_name(first_name: str | None, last_name: str | None) -> str:
	return " ".join(part for part in (first_name, last_name) if part)


def escape(text: str) -> str:
	"""Экранирует текст для сообщений с HTML-разметкой."""
	return html.escape(text, quote=False)


def bold(text: str) -> str:
	return f"<b>{escape(text.strip())}</b>"


def step_header(language: str, step: int) -> str:
	"""Строка «Шаг N из 3» для первой настройки бота (HTML)."""
	return bold(STEP_LABELS.get(language, STEP_LABELS["ru"]).format(step=step))


def no_data_text(language: str) -> str:
	"""Ответ, когда по запросу нет информации."""
	return f"📭 {NO_DATA_TEXTS.get(language, NO_DATA_TEXTS['ru'])}"


def no_data_card(language: str, title: str) -> str:
	"""Заголовок раздела и «Данных нет» (HTML)."""
	return f"{bold(title)}\n\n{no_data_text(language)}"


def selected_colony_name(context: ContextTypes.DEFAULT_TYPE, language: str) -> str:
	"""Название выбранной колонии на языке пользователя."""
	labels = COLONY_GROUP_LABELS.get(language, COLONY_GROUP_LABELS["ru"])
	return labels[COLONY_GROUPS.index(context.user_data["colony"])]


def menu_screen(
	context: ContextTypes.DEFAULT_TYPE,
	section: str = "root",
) -> tuple[str, ReplyKeyboardMarkup | None]:
	"""Текст (HTML) и клавиатура экрана меню колонии: главного, «Информации» или «Услуг»."""
	language = user_language(context)
	info_label, services_label, _ = MENU_SECTION_BUTTONS.get(language, MENU_SECTION_BUTTONS["ru"])
	text = MENU_SECTION_TEXTS.get(language, MENU_SECTION_TEXTS["ru"])[section].format(
		colony=escape(selected_colony_name(context, language)),
		info=bold(info_label),
		services=bold(services_label),
	)
	keyboard = colony_location_reply_keyboard(language, context.user_data["colony"], section)
	return text, keyboard


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
