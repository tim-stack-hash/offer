"""Приём предложений и жалоб пользователей и отправка в отдельную группу."""

from __future__ import annotations

import re

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import get_feedback_chat_id
from bot.content.texts import (
	FEEDBACK_BUTTON_TEXT,
	FEEDBACK_CATEGORY_BUTTONS,
	FEEDBACK_CATEGORY_PROMPTS,
	FEEDBACK_CANCELLED_TEXTS,
	FEEDBACK_MESSAGE_PROMPTS,
	FEEDBACK_SUCCESS_TEXTS,
	FEEDBACK_TOO_LONG_TEXTS,
)
from bot.database import get_user_phone_number, register_support_message
from bot.handlers.support import return_user_keyboard, support_cancel_pattern
from bot.keyboards import feedback_category_keyboard, support_cancel_keyboard

FEEDBACK_CATEGORY = 1
FEEDBACK_MESSAGE = 2
MAX_FEEDBACK_MESSAGE_LENGTH = 3500


async def start_feedback(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Предлагает пользователю выбрать предложение или жалобу."""
	message = update.effective_message
	if not message:
		return ConversationHandler.END

	language = context.user_data.get("language", "ru")
	context.user_data.pop("feedback_category", None)
	await message.reply_text(
		FEEDBACK_CATEGORY_PROMPTS.get(language, FEEDBACK_CATEGORY_PROMPTS["ru"]),
		reply_markup=feedback_category_keyboard(language),
	)
	return FEEDBACK_CATEGORY


async def select_feedback_category(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Сохраняет выбранную категорию и просит написать сообщение."""
	message = update.effective_message
	if not message or not message.text:
		return FEEDBACK_CATEGORY

	category = None
	for language_buttons in FEEDBACK_CATEGORY_BUTTONS.values():
		if message.text.strip() == language_buttons[0]:
			category = "proposal"
			break
		if message.text.strip() == language_buttons[1]:
			category = "complaint"
			break
	if category is None:
		language = context.user_data.get("language", "ru")
		await message.reply_text(
			FEEDBACK_CATEGORY_PROMPTS.get(language, FEEDBACK_CATEGORY_PROMPTS["ru"]),
			reply_markup=feedback_category_keyboard(language),
		)
		return FEEDBACK_CATEGORY

	context.user_data["feedback_category"] = category
	language = context.user_data.get("language", "ru")
	await message.reply_text(
		FEEDBACK_MESSAGE_PROMPTS.get(
			language,
			FEEDBACK_MESSAGE_PROMPTS["ru"],
		)[category],
		reply_markup=support_cancel_keyboard(language),
	)
	return FEEDBACK_MESSAGE


async def send_feedback_message(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Отправляет текст предложения или жалобы в настроенную группу."""
	message = update.effective_message
	user = update.effective_user
	if not message or not message.text or not user:
		return FEEDBACK_MESSAGE

	language = context.user_data.get("language", "ru")
	if len(message.text.encode("utf-16-le")) // 2 > MAX_FEEDBACK_MESSAGE_LENGTH:
		await message.reply_text(
			FEEDBACK_TOO_LONG_TEXTS.get(language, FEEDBACK_TOO_LONG_TEXTS["ru"]),
			reply_markup=support_cancel_keyboard(language),
		)
		return FEEDBACK_MESSAGE

	category = context.user_data.get("feedback_category")
	if category not in ("proposal", "complaint"):
		await message.reply_text(
			FEEDBACK_CATEGORY_PROMPTS.get(language, FEEDBACK_CATEGORY_PROMPTS["ru"]),
			reply_markup=feedback_category_keyboard(language),
		)
		return FEEDBACK_CATEGORY

	category_index = 0 if category == "proposal" else 1
	category_label = FEEDBACK_CATEGORY_BUTTONS.get(
		language,
		FEEDBACK_CATEGORY_BUTTONS["ru"],
	)[category_index]
	name = " ".join(part for part in (user.first_name, user.last_name) if part)
	username = f"@{user.username}" if user.username else "не указан"
	phone_number = get_user_phone_number(user.id) or "не указан"
	report = (
		f"{category_label}\n"
		f"Пользователь: {name or 'не указано'}\n"
		f"Username: {username}\n"
		f"Telegram ID: {user.id}\n"
		f"Телефон: {phone_number}\n\n"
		f"{message.text}"
	)
	feedback_chat_id = get_feedback_chat_id()
	feedback_message = await context.bot.send_message(
		chat_id=feedback_chat_id,
		text=report,
	)
	register_support_message(feedback_chat_id, feedback_message.message_id, user.id)
	context.user_data.pop("feedback_category", None)
	await message.reply_text(
		FEEDBACK_SUCCESS_TEXTS.get(language, FEEDBACK_SUCCESS_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END


async def cancel_feedback(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Отменяет отправку предложения или жалобы."""
	message = update.effective_message
	if not message:
		return ConversationHandler.END

	language = context.user_data.get("language", "ru")
	context.user_data.pop("feedback_category", None)
	await message.reply_text(
		FEEDBACK_CANCELLED_TEXTS.get(language, FEEDBACK_CANCELLED_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END


def feedback_button_pattern() -> str:
	"""Создаёт regexp для локализованных кнопок предложений и жалоб."""
	return "^(?:" + "|".join(
		re.escape(text) for text in FEEDBACK_BUTTON_TEXT.values()
	) + ")$"


def feedback_category_pattern() -> str:
	"""Создаёт regexp для локализованных кнопок выбора категории."""
	return "^(?:" + "|".join(
		re.escape(text)
		for buttons in FEEDBACK_CATEGORY_BUTTONS.values()
		for text in buttons
	) + ")$"


def feedback_cancel_pattern() -> str:
	"""Создаёт regexp для локализованных кнопок отмены."""
	return support_cancel_pattern()
