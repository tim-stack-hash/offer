"""Обновление короткого описания бота счётчиком пользователей."""

from __future__ import annotations

import asyncio

from telegram import Bot

from bot.config import BOT_SHORT_DESCRIPTION_LIMIT, USER_COUNT_DESCRIPTION_PREFIX
from bot.database.users import get_user_count

# Защищает обновление короткого описания бота от параллельных гонок между запросами.
profile_description_lock = asyncio.Lock()


async def update_profile_user_count(bot: Bot) -> None:
	"""Обновляет короткое описание бота, вставляя туда актуальное количество пользователей."""
	async with profile_description_lock:
		user_count = get_user_count()
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
