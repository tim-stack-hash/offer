"""Плановые приглашения посмотреть инструкции по переводу денег."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import time, timedelta, timezone

from telegram import Bot, Message, Update
from telegram.error import BadRequest, TelegramError
from telegram.ext import Application, ContextTypes

from bot.config import MONEY_TRANSFER_MEDIA_PATHS
from bot.content.texts import MONEY_TRANSFER_PROMPT_TEXTS, MONEY_TRANSFER_SENDING_TEXTS
from bot.database import (
	delete_cached_media_file_id,
	get_cached_media_file_id,
	get_registered_users,
	save_cached_media_file_id,
)
from bot.keyboards import money_transfer_confirmation_keyboard

LOGGER = logging.getLogger(__name__)
LOCAL_TIMEZONE = timezone(timedelta(hours=5))
MONEY_TRANSFER_ACTION_THRESHOLD = 20
NOTIFICATION_HOURS = (8, 20)
MEDIA_READ_TIMEOUT_SECONDS = 600
MEDIA_WRITE_TIMEOUT_SECONDS = 600


async def send_money_transfer_prompt(
	bot: Bot,
	chat_id: int,
	language: str,
) -> None:
	"""Отправляет вопрос с кнопками подтверждения."""
	await bot.send_message(
		chat_id=chat_id,
		text=MONEY_TRANSFER_PROMPT_TEXTS.get(
			language,
			MONEY_TRANSFER_PROMPT_TEXTS["ru"],
		),
		reply_markup=money_transfer_confirmation_keyboard(language),
	)


async def _send_instruction_media(bot: Bot, chat_id: int) -> None:
	"""Отправляет изображение и затем три видео в настроенном порядке."""
	failed_media: list[str] = []
	for media_index, media_path in enumerate(MONEY_TRANSFER_MEDIA_PATHS):
		try:
			await _send_cached_or_upload(bot, chat_id, media_path, media_index == 0)
		except (TelegramError, OSError):
			LOGGER.exception(
				"Failed to send money-transfer media %s to user %s",
				media_path,
				chat_id,
			)
			failed_media.append(os.path.basename(media_path))

	if not failed_media:
		await bot.send_message(chat_id=chat_id, text="Готово, все материалы отправлены.")


async def _send_cached_or_upload(
	bot: Bot,
	chat_id: int,
	media_path: str,
	is_photo: bool,
) -> None:
	"""Отправляет сохранённый файл Telegram или загружает и кеширует локальный файл."""
	file_size = os.path.getsize(media_path)
	file_id = get_cached_media_file_id(media_path, file_size)
	timeout_options = {
		"read_timeout": MEDIA_READ_TIMEOUT_SECONDS,
		"write_timeout": MEDIA_WRITE_TIMEOUT_SECONDS,
	}

	if file_id:
		try:
			if is_photo:
				message = await bot.send_photo(
					chat_id=chat_id,
					photo=file_id,
					**timeout_options,
				)
			else:
				message = await bot.send_video(
					chat_id=chat_id,
					video=file_id,
					supports_streaming=True,
					**timeout_options,
				)
			_cache_sent_media(media_path, file_size, message, is_photo)
			return
		except BadRequest:
			LOGGER.warning("Cached Telegram file_id is invalid for %s", media_path)
			delete_cached_media_file_id(media_path)

	with open(media_path, "rb") as media_file:
		if is_photo:
			message = await bot.send_photo(
				chat_id=chat_id,
				photo=media_file,
				**timeout_options,
			)
		else:
			message = await bot.send_video(
				chat_id=chat_id,
				video=media_file,
				supports_streaming=True,
				**timeout_options,
			)

	_cache_sent_media(media_path, file_size, message, is_photo)


def _cache_sent_media(
	media_path: str,
	file_size: int,
	message: Message,
	is_photo: bool,
) -> None:
	"""Сохраняет file_id, полученный от Telegram после успешной отправки."""
	if is_photo:
		file_id = message.photo[-1].file_id if message.photo else None
	else:
		file_id = message.video.file_id if message.video else None
	if file_id:
		save_cached_media_file_id(media_path, file_size, file_id)


async def handle_money_transfer_callback(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Отправляет инструкции после подтверждения и закрывает кнопки."""
	query = update.callback_query
	if not query or not query.data:
		return

	await query.answer()
	if query.message:
		await query.edit_message_reply_markup(reply_markup=None)

	if query.data == "money_transfer:yes" and update.effective_chat:
		await context.bot.send_message(
			chat_id=update.effective_chat.id,
			text=MONEY_TRANSFER_SENDING_TEXTS.get(
				context.user_data.get("language", "ru"),
				MONEY_TRANSFER_SENDING_TEXTS["ru"],
			),
		)
		await _send_instruction_media(context.bot, update.effective_chat.id)


async def send_scheduled_money_transfer_prompts(
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Отправляет приглашение всем зарегистрированным пользователям."""
	for user_id, language in get_registered_users():
		try:
			await send_money_transfer_prompt(context.bot, user_id, language)
		except TelegramError:
			LOGGER.exception(
				"Failed to send scheduled money-transfer prompt to user %s",
				user_id,
			)
		await asyncio.sleep(0.05)


def schedule_money_transfer_notifications(application: Application) -> None:
	"""Настраивает ежедневные рассылки на 08:00 и 20:00 по UTC+05:00."""
	if application.job_queue is None:
		raise RuntimeError(
			'Install python-telegram-bot with the "job-queue" extra to schedule notifications'
		)

	for hour in NOTIFICATION_HOURS:
		application.job_queue.run_daily(
			send_scheduled_money_transfer_prompts,
			time=time(hour=hour, tzinfo=LOCAL_TIMEZONE),
			name=f"money-transfer-prompt-{hour:02d}",
		)
