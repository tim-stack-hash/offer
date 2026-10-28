"""Отправка локальных медиафайлов с повторным использованием Telegram file_id.

После первой загрузки Telegram возвращает file_id, по которому тот же файл можно
отправлять мгновенно, без повторной загрузки. Кеш хранится в базе и сбрасывается,
если файл на диске изменился (по размеру) или Telegram отклонил file_id.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from contextlib import ExitStack

from telegram import Bot, InputMediaPhoto, Message
from telegram.constants import ChatAction
from telegram.error import BadRequest, TelegramError

from bot.config import media_cache_key
from bot.database import (
	delete_cached_media_file_id,
	get_cached_media_file_id,
	save_cached_media_file_id,
)

LOGGER = logging.getLogger(__name__)

MEDIA_READ_TIMEOUT_SECONDS = 600
MEDIA_WRITE_TIMEOUT_SECONDS = 600
UPLOAD_TIMEOUTS = {
	"read_timeout": MEDIA_READ_TIMEOUT_SECONDS,
	"write_timeout": MEDIA_WRITE_TIMEOUT_SECONDS,
}


async def _show_upload_status(bot: Bot, chat_id: int, is_photo: bool) -> None:
	"""Показывает пользователю «отправляет фото / видео…», пока файл загружается."""
	try:
		await bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO if is_photo else ChatAction.UPLOAD_VIDEO)
	except TelegramError:
		LOGGER.debug("Could not show upload status to %s", chat_id, exc_info=True)


async def _send(bot: Bot, chat_id: int, media: object, is_photo: bool) -> Message:
	if is_photo:
		return await bot.send_photo(chat_id=chat_id, photo=media, **UPLOAD_TIMEOUTS)
	return await bot.send_video(
		chat_id=chat_id,
		video=media,
		supports_streaming=True,
		**UPLOAD_TIMEOUTS,
	)


def _sent_file_id(message: Message, is_photo: bool) -> str | None:
	if is_photo:
		return message.photo[-1].file_id if message.photo else None
	return message.video.file_id if message.video else None


async def send_cached_media(bot: Bot, chat_id: int, media_path: str, is_photo: bool) -> None:
	"""Отправляет фото или видео по сохранённому file_id либо загружает файл и запоминает file_id.

	Бросает OSError, если файла нет, и TelegramError, если Telegram отклонил отправку.
	"""
	file_size = os.path.getsize(media_path)
	cache_key = media_cache_key(media_path)
	file_id = get_cached_media_file_id(cache_key, file_size)

	if file_id:
		try:
			await _send(bot, chat_id, file_id, is_photo)
			return
		except BadRequest:
			LOGGER.warning("Cached Telegram file_id is invalid for %s", media_path)
			delete_cached_media_file_id(cache_key)

	await _show_upload_status(bot, chat_id, is_photo)
	with open(media_path, "rb") as media_file:
		message = await _send(bot, chat_id, media_file, is_photo)

	new_file_id = _sent_file_id(message, is_photo)
	if new_file_id:
		save_cached_media_file_id(cache_key, file_size, new_file_id)


async def send_cached_photo_album(bot: Bot, chat_id: int, photo_paths: Sequence[str]) -> None:
	"""Отправляет 2–10 фото одним альбомом, переиспользуя file_id уже загруженных фото.

	Бросает OSError, если какого-то файла нет, и TelegramError при ошибке Telegram.
	"""
	cache_keys = [media_cache_key(path) for path in photo_paths]
	file_sizes = [os.path.getsize(path) for path in photo_paths]
	file_ids = [
		get_cached_media_file_id(cache_key, file_size)
		for cache_key, file_size in zip(cache_keys, file_sizes)
	]

	if all(file_ids):
		try:
			await bot.send_media_group(
				chat_id=chat_id,
				media=[InputMediaPhoto(media=file_id) for file_id in file_ids],
			)
			return
		except BadRequest:
			LOGGER.warning("Cached photo album is invalid, uploading the files again")
			for cache_key in cache_keys:
				delete_cached_media_file_id(cache_key)

	await _show_upload_status(bot, chat_id, is_photo=True)
	with ExitStack() as open_files:
		media = [
			InputMediaPhoto(media=open_files.enter_context(open(path, "rb")))
			for path in photo_paths
		]
		messages = await bot.send_media_group(chat_id=chat_id, media=media, **UPLOAD_TIMEOUTS)

	for cache_key, file_size, message in zip(cache_keys, file_sizes, messages):
		file_id = _sent_file_id(message, is_photo=True)
		if file_id:
			save_cached_media_file_id(cache_key, file_size, file_id)
