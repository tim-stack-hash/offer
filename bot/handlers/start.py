"""Обработчик команды /start — первого сообщения, которое видит пользователь."""

from __future__ import annotations

from telegram import Message, Update
from telegram.ext import ContextTypes

from bot.database import register_user, update_profile_user_count
from bot.keyboards import language_selection_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Регистрирует пользователя в базе и показывает клавиатуру выбора языка."""
	message = update.message
	if not message and update.callback_query:
		await update.callback_query.answer()
		if isinstance(update.callback_query.message, Message):
			message = update.callback_query.message

	if message:
		user = update.effective_user
		is_new_user = False
		if user:
			is_new_user = register_user(
				user.id,
				user.username,
				user.first_name,
				user.last_name,
			)
		context.user_data.pop("changing_language", None)
		await message.reply_text(
			"🌐 Выберите язык / Tilni tanlang:",
			reply_markup=language_selection_keyboard(),
		)
		if user and is_new_user:
			await update_profile_user_count(context.bot)
