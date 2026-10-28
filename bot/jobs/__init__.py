"""Фоновые задачи бота, выполняемые по расписанию."""

from __future__ import annotations

from telegram.ext import Application, ContextTypes

from bot.jobs.money_transfer import schedule_money_transfer_notifications
from bot.services.profile import update_profile_user_count

PROFILE_COUNTER_INTERVAL_SECONDS = 15 * 60


async def _refresh_profile_counter(context: ContextTypes.DEFAULT_TYPE) -> None:
	await update_profile_user_count(context.bot)


def schedule_jobs(application: Application) -> None:
	"""Регистрирует все периодические задачи."""
	if application.job_queue is None:
		raise RuntimeError(
			'Install python-telegram-bot with the "job-queue" extra to run scheduled jobs'
		)

	schedule_money_transfer_notifications(application)
	application.job_queue.run_repeating(
		_refresh_profile_counter,
		interval=PROFILE_COUNTER_INTERVAL_SECONDS,
		first=5,
		name="profile-user-counter",
	)
