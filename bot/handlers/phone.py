"""Запрос, проверка и сохранение номера телефона пользователя."""

from __future__ import annotations

import logging
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.content.texts import COLONY_PROMPTS, PHONE_PROMPTS
from bot.database import save_user_phone_number
from bot.handlers.common import user_language
from bot.keyboards import (
	change_language_keyboard,
	colony_group_keyboard,
	contact_request_keyboard,
)

PHONE_REQUIRED = 1
LOGGER = logging.getLogger(__name__)


async def remind_phone_required(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Повторяет просьбу отправить телефон и удерживает пользователя на этом шаге."""
	message = update.effective_message
	if not message:
		return PHONE_REQUIRED

	language = user_language(context)
	texts = PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])
	await message.reply_text(
		texts["retry"],
		reply_markup=contact_request_keyboard(language),
	)
	return PHONE_REQUIRED


async def receive_phone_number(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Сохраняет номер телефона пользователя и переходит к выбору колонии."""
	message = update.message
	user = update.effective_user
	if not message or not message.contact or not user:
		return PHONE_REQUIRED

	language = user_language(context)
	texts = PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])
	# Telegram normally includes user_id for a contact shared via request_contact,
	# but some clients/updates omit it. The sender identity is still known; only
	# reject a contact when Telegram explicitly identifies a different person.
	if message.contact.user_id is not None and message.contact.user_id != user.id:
		await message.reply_text(
			texts["retry"],
			reply_markup=contact_request_keyboard(language),
		)
		return PHONE_REQUIRED

	try:
		save_user_phone_number(user.id, message.contact.phone_number)
	except sqlite3.Error:
		LOGGER.exception("Failed to save phone number for user %s", user.id)
		await message.reply_text(
			texts["retry"],
			reply_markup=contact_request_keyboard(language),
		)
		return PHONE_REQUIRED

	context.user_data["phone_number"] = message.contact.phone_number
	await message.reply_text(
		texts["received"],
		reply_markup=change_language_keyboard(language),
	)
	await message.reply_text(
		COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
		reply_markup=colony_group_keyboard(language),
	)
	return ConversationHandler.END
