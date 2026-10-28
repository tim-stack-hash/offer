"""Обновление короткого описания бота счётчиком пользователей."""

from __future__ import annotations

import asyncio
import logging

from telegram import Bot
from telegram.error import TelegramError

from bot.config import BOT_SHORT_DESCRIPTION_LIMIT, USER_COUNT_DESCRIPTION_PREFIX
from bot.database import get_user_count

LOGGER = logging.getLogger(__name__)

# Защищает обновление описания от параллельных вызовов.
_profile_description_lock = asyncio.Lock()
_last_published_count: int | None = None


async def update_profile_user_count(bot: Bot) -> None:
	"""Вставляет актуальное число пользователей в короткое описание бота.

	Telegram жёстко ограничивает частоту setMyShortDescription, поэтому запрос
	отправляется только когда число пользователей изменилось.
	"""
	global _last_published_count
	async with _profile_description_lock:
		user_count = get_user_count()
		if user_count == _last_published_count:
			return

		try:
			current_description = await bot.get_my_short_description()
			base_description = "\n".join(
				line for line in current_description.short_description.splitlines()
				if not line.startswith(USER_COUNT_DESCRIPTION_PREFIX)
			).strip()
			count_line = f"{USER_COUNT_DESCRIPTION_PREFIX}{user_count}"
			available_base_length = BOT_SHORT_DESCRIPTION_LIMIT - len(count_line) - 1
			base_description = base_description[:max(0, available_base_length)].rstrip()
			short_description = (
				f"{count_line}\n{base_description}"
				if base_description
				else count_line
			)
			await bot.set_my_short_description(short_description)
		except TelegramError:
			LOGGER.warning("Could not update bot short description", exc_info=True)
			return
		_last_published_count = user_count
