"""Предложения и жалобы пользователей."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import get_feedback_chat_id
from bot.content.texts import (
	FEEDBACK_CANCELLED_TEXTS,
	FEEDBACK_CATEGORY_BUTTONS,
	FEEDBACK_CATEGORY_PROMPTS,
	FEEDBACK_MESSAGE_PROMPTS,
	FEEDBACK_SUCCESS_TEXTS,
	FEEDBACK_TOO_LONG_TEXTS,
)
from bot.handlers.common import return_user_keyboard, user_language
from bot.handlers.support import DELIVERY_ERROR_TEXTS, forward_user_report, is_too_long
from bot.keyboards import feedback_category_keyboard, support_cancel_keyboard

FEEDBACK_CATEGORY = 1
FEEDBACK_MESSAGE = 2
CATEGORIES = ("proposal", "complaint")


def _category_by_label(text: str) -> str | None:
	text = text.strip()
	for buttons in FEEDBACK_CATEGORY_BUTTONS.values():
		for category, label in zip(CATEGORIES, buttons):
			if text == label:
				return category
	return None


async def _ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	language = user_language(context)
	await update.effective_message.reply_text(
		FEEDBACK_CATEGORY_PROMPTS.get(language, FEEDBACK_CATEGORY_PROMPTS["ru"]),
		reply_markup=feedback_category_keyboard(language),
	)
	return FEEDBACK_CATEGORY


async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Предлагает выбрать: предложение или жалоба."""
	if not update.effective_message:
		return ConversationHandler.END

	context.user_data.pop("feedback_category", None)
	return await _ask_category(update, context)


async def select_feedback_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Запоминает категорию и просит написать сообщение."""
	message = update.effective_message
	if not message or not message.text:
		return FEEDBACK_CATEGORY

	category = _category_by_label(message.text)
	if category is None:
		return await _ask_category(update, context)

	context.user_data["feedback_category"] = category
	language = user_language(context)
	await message.reply_text(
		FEEDBACK_MESSAGE_PROMPTS.get(language, FEEDBACK_MESSAGE_PROMPTS["ru"])[category],
		reply_markup=support_cancel_keyboard(language),
	)
	return FEEDBACK_MESSAGE


async def send_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Отправляет предложение или жалобу в группу обратной связи."""
	message = update.effective_message
	user = update.effective_user
	if not message or not message.text or not user:
		return FEEDBACK_MESSAGE

	language = user_language(context)
	if is_too_long(message.text):
		await message.reply_text(
			FEEDBACK_TOO_LONG_TEXTS.get(language, FEEDBACK_TOO_LONG_TEXTS["ru"]),
			reply_markup=support_cancel_keyboard(language),
		)
		return FEEDBACK_MESSAGE

	category = context.user_data.get("feedback_category")
	if category not in CATEGORIES:
		return await _ask_category(update, context)

	title = FEEDBACK_CATEGORY_BUTTONS.get(language, FEEDBACK_CATEGORY_BUTTONS["ru"])[
		CATEGORIES.index(category)
	]
	delivered = await forward_user_report(context, get_feedback_chat_id(), title, user, message.text)
	if not delivered:
		await message.reply_text(
			DELIVERY_ERROR_TEXTS.get(language, DELIVERY_ERROR_TEXTS["ru"]),
			reply_markup=support_cancel_keyboard(language),
		)
		return FEEDBACK_MESSAGE

	context.user_data.pop("feedback_category", None)
	await message.reply_text(
		FEEDBACK_SUCCESS_TEXTS.get(language, FEEDBACK_SUCCESS_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END


async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Отменяет отправку предложения или жалобы."""
	message = update.effective_message
	if not message:
		return ConversationHandler.END

	language = user_language(context)
	context.user_data.pop("feedback_category", None)
	await message.reply_text(
		FEEDBACK_CANCELLED_TEXTS.get(language, FEEDBACK_CANCELLED_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END
