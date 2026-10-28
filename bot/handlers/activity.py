"""Фиксация нажатий кнопок, отправленных боту пользователями."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.content.clothing_regions import CLOTHING_REGIONS
from bot.content.colonies import COLONY_GROUP_LABELS
from bot.content.lawyer_regions import LAWYER_REGIONS
from bot.content.lawyers import LAWYERS
from bot.content.texts import (
	APPLICATION_TYPE_BUTTONS,
	LAWYER_ACTION_BUTTONS,
	LAWYER_REVIEW_MENU_BUTTONS,
)
from bot.database import record_user_action
from bot.handlers.common import user_language
from bot.handlers.money_transfer import (
	MONEY_TRANSFER_ACTION_THRESHOLD,
	send_money_transfer_prompt,
)
from bot.handlers.patterns import BUTTON_LABELS

LOGGER = logging.getLogger(__name__)


def _callback_action(callback_data: str, language: str) -> str:
	"""Преобразует callback-код инлайн-кнопки в читаемое название."""
	if callback_data.startswith("application:"):
		application_type = callback_data.removeprefix("application:")
		button_index = {"long": 0, "short": 1}.get(application_type)
		if button_index is not None:
			return APPLICATION_TYPE_BUTTONS.get(
				language,
				APPLICATION_TYPE_BUTTONS["ru"],
			)[button_index]
	if callback_data.startswith("colonies:select:"):
		try:
			index = int(callback_data.removeprefix("colonies:select:"))
			return f"Выбор колонии: {COLONY_GROUP_LABELS.get(language, COLONY_GROUP_LABELS['ru'])[index]}"
		except (ValueError, IndexError):
			return "Выбор колонии"
	if callback_data.startswith("clothing:region:"):
		region_id = callback_data.removeprefix("clothing:region:")
		region = CLOTHING_REGIONS.get(region_id)
		if region:
			return f"Регион одежды: {region.get(language, region['ru'])}"
	if callback_data.startswith("lawyer:region:"):
		region_id = callback_data.removeprefix("lawyer:region:")
		region = LAWYER_REGIONS.get(region_id)
		if region:
			return f"Регион адвоката: {region.get(language, region['ru'])}"
	if callback_data.startswith("lawyer:"):
		callback_parts = callback_data.split(":", 2)
		if len(callback_parts) != 3:
			return "Кнопка адвоката"
		_, action, lawyer_id = callback_parts
		lawyer = LAWYERS.get(lawyer_id)
		if lawyer and action == "profile":
			return f"Адвокат: {lawyer['name']}"
		if lawyer and action == "call":
			return LAWYER_ACTION_BUTTONS.get(
				language,
				LAWYER_ACTION_BUTTONS["ru"],
			)[1]
		if lawyer and action == "reviews":
			return LAWYER_ACTION_BUTTONS.get(
				language,
				LAWYER_ACTION_BUTTONS["ru"],
			)[0]
		if lawyer and action in ("write_review", "show_reviews"):
			button_index = 0 if action == "write_review" else 1
			return LAWYER_REVIEW_MENU_BUTTONS.get(
				language,
				LAWYER_REVIEW_MENU_BUTTONS["ru"],
			)[button_index]
	if callback_data == "colonies:open":
		return "Открыть список колоний"
	if callback_data == "colonies:location":
		return "Локация колонии"
	return f"Кнопка: {callback_data}"


async def track_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Записывает нажатие известной кнопки или команды, не сохраняя свободный текст."""
	user = update.effective_user
	chat = update.effective_chat
	if not user or user.is_bot or not chat or chat.type != "private":
		return
	if (
		update.callback_query
		and update.callback_query.data
		and update.callback_query.data.startswith(("admin:", "money_transfer:"))
	):
		return

	language = user_language(context)
	if update.callback_query and update.callback_query.data:
		action = _callback_action(update.callback_query.data, language)
	elif update.message and update.message.contact:
		action = "Отправить номер телефона"
	elif update.message and update.message.text:
		text = update.message.text.strip()
		command = text.split(maxsplit=1)[0].split("@", maxsplit=1)[0]
		action = command if command in ("/start", "/menu") else text
		if action not in BUTTON_LABELS:
			return
	else:
		return

	action_count = record_user_action(user.id, action)
	if action_count % MONEY_TRANSFER_ACTION_THRESHOLD == 0:
		try:
			await send_money_transfer_prompt(context.bot, user.id, language)
		except TelegramError:
			LOGGER.warning("Could not send money-transfer prompt to user %s", user.id, exc_info=True)
