"""Приём обращений пользователей и пересылка в канал поддержки."""

from __future__ import annotations

import logging
import re

from telegram import ReplyKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import (
	SUPPORT_REPLY_USER_IDS,
	get_feedback_chat_id,
	get_support_chat_id,
	is_admin,
)
from bot.content.colonies import COLONY_COORDINATES
from bot.content.texts import (
	SUPPORT_CANCEL_BUTTONS,
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
from bot.keyboards import (
	change_language_keyboard,
	colony_location_reply_keyboard,
	contact_request_keyboard,
	language_selection_keyboard,
	support_cancel_keyboard,
)

SUPPORT_MESSAGE = 1
MAX_SUPPORT_MESSAGE_LENGTH = 3500
LOGGER = logging.getLogger(__name__)


def return_user_keyboard(context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
	"""Восстанавливает клавиатуру, которая соответствует текущему шагу пользователя."""
	language = context.user_data.get("language", "ru")
	colony = context.user_data.get("colony")
	if not context.user_data.get("language"):
		return language_selection_keyboard()
	if colony in COLONY_COORDINATES:
		keyboard = colony_location_reply_keyboard(
			language, colony, context.user_data.get("menu_section", "root")
		)
		if keyboard:
			return keyboard
	return change_language_keyboard(language)


async def start_support(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Предлагает пользователю описать проблему."""
	message = update.effective_message
	if not message:
		return ConversationHandler.END

	language = context.user_data.get("language", "ru")
	await message.reply_text(
		SUPPORT_PROMPTS.get(language, SUPPORT_PROMPTS["ru"]),
		reply_markup=support_cancel_keyboard(language),
	)
	return SUPPORT_MESSAGE


async def send_support_message(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Пересылает текст обращения с данными отправителя в чат поддержки."""
	message = update.effective_message
	user = update.effective_user
	if not message or not message.text or not user:
		return SUPPORT_MESSAGE

	language = context.user_data.get("language", "ru")
	if len(message.text.encode("utf-16-le")) // 2 > MAX_SUPPORT_MESSAGE_LENGTH:
		await message.reply_text(
			SUPPORT_TOO_LONG_TEXTS.get(language, SUPPORT_TOO_LONG_TEXTS["ru"]),
			reply_markup=support_cancel_keyboard(language),
		)
		return SUPPORT_MESSAGE

	name = " ".join(part for part in (user.first_name, user.last_name) if part)
	username = f"@{user.username}" if user.username else "не указан"
	phone_number = get_user_phone_number(user.id) or "не указан"
	report = (
		"🆘 Обращение в поддержку\n"
		f"Пользователь: {name or 'не указано'}\n"
		f"Username: {username}\n"
		f"Telegram ID: {user.id}\n\n"
		f"Телефон: {phone_number}\n\n"
		f"{message.text}"
	)
	support_chat_id = get_support_chat_id()
	support_message = await context.bot.send_message(
		chat_id=support_chat_id,
		text=report,
	)
	register_support_message(support_chat_id, support_message.message_id, user.id)
	await message.reply_text(
		SUPPORT_SUCCESS_TEXTS.get(language, SUPPORT_SUCCESS_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END


async def handle_support_admin_reply(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Пересылает ответ администратора на обращение нужному пользователю."""
	message = update.effective_message
	user = update.effective_user
	chat = update.effective_chat
	if not message or not user or not chat or not message.reply_to_message:
		return
	if chat.id not in (get_support_chat_id(), get_feedback_chat_id()) or (
		not is_admin(user.id) and user.id not in SUPPORT_REPLY_USER_IDS
	):
		return

	recipient_id = get_support_message_recipient(
		chat.id,
		message.reply_to_message.message_id,
	)
	if recipient_id is None:
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


async def cancel_support(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Отменяет ввод обращения и возвращает пользовательскую клавиатуру."""
	message = update.effective_message
	if not message:
		return ConversationHandler.END

	language = context.user_data.get("language", "ru")
	await message.reply_text(
		SUPPORT_CANCELLED_TEXTS.get(language, SUPPORT_CANCELLED_TEXTS["ru"]),
		reply_markup=return_user_keyboard(context),
	)
	return ConversationHandler.END


def support_cancel_pattern() -> str:
	"""Создаёт regexp для локализованных кнопок отмены."""
	return "^(?:" + "|".join(
		re.escape(text) for text in SUPPORT_CANCEL_BUTTONS.values()
	) + ")$"
