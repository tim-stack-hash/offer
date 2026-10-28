"""Перевод денег: ссылки на приложения и видеоинструкции по запросу пользователя."""

from __future__ import annotations

import logging
import os

from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.config import MONEY_TRANSFER_MEDIA
from bot.content.texts import (
	MONEY_TRANSFER_PROMPT_TEXTS,
	MONEY_TRANSFER_SENDING_TEXTS,
	TRANSFER_MONEY_PROMPTS,
)
from bot.handlers.common import user_language
from bot.keyboards import money_transfer_apps_keyboard, money_transfer_confirmation_keyboard
from bot.services.media import send_cached_media

LOGGER = logging.getLogger(__name__)

# Через сколько учтённых действий пользователю предлагаются инструкции.
MONEY_TRANSFER_ACTION_THRESHOLD = 20

INSTRUCTIONS_SENT_TEXTS = {
	"ru": "✅ Готово, все материалы отправлены.",
	"uz": "✅ Tayyor, barcha materiallar yuborildi.",
	"uz_cyr": "✅ Тайёр, барча материаллар юборилди.",
}


async def send_money_transfer_prompt(bot: Bot, chat_id: int, language: str) -> None:
	"""Спрашивает, прислать ли инструкции по переводу (кнопки «Да» / «Нет»)."""
	await bot.send_message(
		chat_id=chat_id,
		text=MONEY_TRANSFER_PROMPT_TEXTS.get(language, MONEY_TRANSFER_PROMPT_TEXTS["ru"]),
		reply_markup=money_transfer_confirmation_keyboard(language),
	)


async def handle_money_transfer_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Кнопка «Перевести деньги» в меню: приложения для перевода и предложение инструкций."""
	message = update.effective_message
	if not message:
		return

	language = user_language(context)
	await message.reply_text(
		TRANSFER_MONEY_PROMPTS.get(language, TRANSFER_MONEY_PROMPTS["ru"]),
		reply_markup=money_transfer_apps_keyboard(),
	)
	await send_money_transfer_prompt(context.bot, message.chat_id, language)


async def _send_instruction_media(bot: Bot, chat_id: int, language: str) -> None:
	"""Отправляет фото и видео по порядку; сбой одного файла не останавливает остальные."""
	sent_any = False
	for media_path, is_photo in MONEY_TRANSFER_MEDIA:
		if not os.path.exists(media_path):
			LOGGER.warning("Money-transfer media file is missing: %s", media_path)
			continue
		try:
			await send_cached_media(bot, chat_id, media_path, is_photo)
			sent_any = True
		except (TelegramError, OSError):
			LOGGER.exception("Failed to send money-transfer media %s to user %s", media_path, chat_id)

	if sent_any:
		await bot.send_message(
			chat_id=chat_id,
			text=INSTRUCTIONS_SENT_TEXTS.get(language, INSTRUCTIONS_SENT_TEXTS["ru"]),
		)


async def handle_money_transfer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Ответ на «Да» / «Нет»: убирает кнопки и при согласии отправляет инструкции."""
	query = update.callback_query
	chat = update.effective_chat
	if not query or not query.data or not chat:
		return

	await query.answer()
	try:
		await query.edit_message_reply_markup(reply_markup=None)
	except TelegramError:
		# Кнопки уже убраны (повторное нажатие) — повторно ничего не отправляем.
		return

	if query.data == "money_transfer:yes":
		language = user_language(context)
		await context.bot.send_message(
			chat_id=chat.id,
			text=MONEY_TRANSFER_SENDING_TEXTS.get(language, MONEY_TRANSFER_SENDING_TEXTS["ru"]),
		)
		await _send_instruction_media(context.bot, chat.id, language)
