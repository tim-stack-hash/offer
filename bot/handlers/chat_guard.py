"""Не даёт боту реагировать на кнопки и сообщения в посторонних группах."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ApplicationHandlerStop, ContextTypes

from bot.config import get_feedback_chat_id, get_support_chat_id


async def block_group_interaction(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Останавливает обработку обновлений из групп, где бот не должен работать."""
	chat = update.effective_chat
	if not chat or chat.type == "private":
		return

	if update.chat_member:
		return

	if chat.id in (get_support_chat_id(), get_feedback_chat_id()):
		return

	raise ApplicationHandlerStop
