"""Обращения в поддержку и ответы администраторов на них."""

from __future__ import annotations

import logging

from telegram import Update, User
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import (
	MAX_USER_MESSAGE_LENGTH,
	SUPPORT_REPLY_USER_IDS,
	get_feedback_chat_id,
	get_support_chat_id,
	is_admin,
)
from bot.content.texts import (
	DELIVERY_ERROR_TEXTS,
	SUPPORT_CANCELLED_TEXTS,
	SUPPORT_PROMPTS,
	SUPPORT_SUCCESS_TEXTS,
	SUPPORT_TOO_LONG_TEXTS,
)
from bot.database import (
	get_support_message_recipient,
	get_user_phone_number,
	register_support_message,
)
from bot.handlers.common import full_name, return_user_keyboard, telegram_text_length, user_language
from bot.keyboards import support_cancel_keyboard

SUPPORT_MESSAGE = 1
LOGGER = logging.getLogger(__name__)

def is_too_long(text: str) -> bool:
	return telegram_text_length(text) > MAX_USER_MESSAGE_LENGTH


async def forward_user_report(
	context: ContextTypes.DEFAULT_TYPE,
	chat_id: int,
	title: str,
	user: User,
	text: str,
) -> bool:
	"""Отправляет обращение пользователя в служебную группу и запоминает автора для ответа."""
	username = f"@{user.username}" if user.username else "не указан"
	phone_number = get_user_phone_number(user.id) or "не указан"
	report = (
		f"{title}\n"
		f"Пользователь: {full_name(user.first_name, user.last_name) or 'не указано'}\n"
		f"Username: {username}\n"
		f"Telegram ID: {user.id}\n"
		f"Телефон: {phone_number}\n\n"
		f"{text}"
	)
	try:
		sent = await context.bot.send_message(chat_id=chat_id, text=report)
	except TelegramError:
		LOGGER.exception("Failed to forward report from user %s to chat %s", user.id, chat_id)
		return False

	register_support_message(chat_id, sent.message_id, user.id)
	return True


async def start_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Просит пользователя описать проблему."""
	message = update.effective_message
	if not message:
		return ConversationHandler.END

	language = user_language(context)
	await message.reply_text(
		SUPPORT_PROMPTS.get(language, SUPPORT_PROMPTS["ru"]),
		reply_markup=support_cancel_keyboard(language),
	)
	return SUPPORT_MESSAGE


async def send_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Пересылает текст обращения в группу поддержки."""
	message = update.effective_message
	user = update.effective_user
	if not message or not message.text or not user:
		return SUPPORT_MESSAGE

	language = user_language(context)
	if is_too_long(message.text):
		await message.reply_text(
			SUPPORT_TOO_LONG_TEXTS.get(language, SUPPORT_TOO_LONG_TEXTS["ru"]),
			reply_markup=support_cancel_keyboard(language),
		)
		return SUPPORT_MESSAGE

	delivered = await forward_user_report(
		context, get_support_chat_id(), "🆘 Обращение в поддержку", user, message.text
	)
	if not delivered:
		await message.reply_text(
			DELIVERY_ERROR_TEXTS.get(language, DELIVERY_ERROR_TEXTS["ru"]),
			reply_markup=support_cancel_keyboard(language),
		)
		return SUPPORT_MESSAGE

	await message.reply_text(
		SUPPORT_SUCCESS_TEXTS.get(language, SUPPORT_SUCCESS_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END


async def remind_text_only(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Пользователь прислал не текст (фото, стикер) — напоминаем, что нужен текст."""
	message = update.effective_message
	if message:
		language = user_language(context)
		await message.reply_text(
			SUPPORT_PROMPTS.get(language, SUPPORT_PROMPTS["ru"]),
			reply_markup=support_cancel_keyboard(language),
		)


async def cancel_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Отменяет ввод обращения и возвращает пользовательскую клавиатуру."""
	message = update.effective_message
	if not message:
		return ConversationHandler.END

	language = user_language(context)
	await message.reply_text(
		SUPPORT_CANCELLED_TEXTS.get(language, SUPPORT_CANCELLED_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END


async def handle_support_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Пересылает ответ администратора (Reply на обращение) нужному пользователю."""
	message = update.effective_message
	user = update.effective_user
	chat = update.effective_chat
	if not message or not user or not chat or not message.reply_to_message:
		return
	if chat.id not in (get_support_chat_id(), get_feedback_chat_id()):
		return
	if not is_admin(user.id) and user.id not in SUPPORT_REPLY_USER_IDS:
		return

	recipient_id = get_support_message_recipient(chat.id, message.reply_to_message.message_id)
	if recipient_id is None:
		# Ответы на обычные сообщения в группе не являются ответами на обращения.
		if message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
			await message.reply_text(
				"Не найдено обращение, на которое вы ответили. "
				"Ответьте именно на сообщение бота с обращением пользователя."
			)
		return

	try:
		await context.bot.copy_message(
			chat_id=recipient_id,
			from_chat_id=chat.id,
			message_id=message.message_id,
		)
	except TelegramError:
		LOGGER.exception(
			"Failed to deliver support reply from admin %s to user %s",
			user.id,
			recipient_id,
		)
		await message.reply_text(
			"Не удалось доставить ответ пользователю. Возможно, он заблокировал бота."
		)
		return

	await message.reply_text("✅ Ответ отправлен пользователю.")
