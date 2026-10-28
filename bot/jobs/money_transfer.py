"""Ежедневная рассылка предложения посмотреть инструкции по переводу денег."""

from __future__ import annotations

import asyncio
import logging
from datetime import time, timedelta

from telegram.error import Forbidden, RetryAfter, TelegramError
from telegram.ext import Application, ContextTypes

from bot.config import LOCAL_TIMEZONE
from bot.database import get_registered_users
from bot.handlers.money_transfer import send_money_transfer_prompt

LOGGER = logging.getLogger(__name__)

NOTIFICATION_HOURS = (8, 20)
# Telegram допускает около 30 сообщений в секунду; держимся с запасом.
SEND_INTERVAL_SECONDS = 0.05


def _retry_delay_seconds(error: RetryAfter) -> float:
	"""retry_after бывает числом или timedelta в зависимости от версии библиотеки."""
	delay = error.retry_after
	return delay.total_seconds() if isinstance(delay, timedelta) else float(delay)


async def send_scheduled_money_transfer_prompts(context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Рассылает приглашение всем зарегистрированным пользователям."""
	sent = blocked = failed = 0
	for user_id, language in get_registered_users():
		for _attempt in range(2):
			try:
				await send_money_transfer_prompt(context.bot, user_id, language)
				sent += 1
			except RetryAfter as error:
				await asyncio.sleep(_retry_delay_seconds(error) + 1)
				continue
			except Forbidden:
				blocked += 1
			except TelegramError:
				failed += 1
				LOGGER.warning("Failed to send scheduled prompt to user %s", user_id, exc_info=True)
			break
		await asyncio.sleep(SEND_INTERVAL_SECONDS)

	LOGGER.info(
		"Money-transfer broadcast finished: sent=%s, blocked=%s, failed=%s",
		sent,
		blocked,
		failed,
	)


def schedule_money_transfer_notifications(application: Application) -> None:
	"""Настраивает рассылки на 08:00 и 20:00 по Ташкенту."""
	for hour in NOTIFICATION_HOURS:
		application.job_queue.run_daily(
			send_scheduled_money_transfer_prompts,
			time=time(hour=hour, tzinfo=LOCAL_TIMEZONE),
			name=f"money-transfer-prompt-{hour:02d}",
		)
