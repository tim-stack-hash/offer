"""Проверка членства пользователя в обязательной группе с кратким кешем."""

from __future__ import annotations

import logging
import time

from telegram import Bot, ChatMemberRestricted
from telegram.error import TelegramError

from bot.config import SUBSCRIPTION_CHAT_ID

LOGGER = logging.getLogger(__name__)

# Подтверждённое членство кешируется, чтобы не дёргать getChatMember на каждое нажатие.
MEMBERSHIP_CACHE_SECONDS = 120
_confirmed_members: dict[int, float] = {}


def is_member_status(member: object) -> bool:
	"""Состоит ли участник в группе (включая ограниченных участников)."""
	return getattr(member, "status", None) in {"creator", "administrator", "member"} or (
		isinstance(member, ChatMemberRestricted) and member.is_member
	)


def is_subscription_chat(chat: object) -> bool:
	"""Относится ли чат к обязательной группе."""
	configured_chat = str(SUBSCRIPTION_CHAT_ID)
	if configured_chat.startswith("@"):
		username = getattr(chat, "username", None) or ""
		return username.lower() == configured_chat[1:].lower()
	try:
		return getattr(chat, "id", None) == int(configured_chat)
	except ValueError:
		return False


def remember_membership(user_id: int, is_member: bool) -> None:
	"""Обновляет кеш по событию вступления или выхода из группы."""
	if is_member:
		_confirmed_members[user_id] = time.monotonic() + MEMBERSHIP_CACHE_SECONDS
	else:
		_confirmed_members.pop(user_id, None)


async def check_membership(bot: Bot, user_id: int) -> bool:
	"""Проверяет членство в группе.

	Если Telegram не дал ответа (сбой сети, у бота нет прав), пользователь
	пропускается: блокировать всех из-за технической ошибки хуже, чем
	временно пропустить проверку. Ошибка при этом пишется в лог.
	"""
	expires_at = _confirmed_members.get(user_id)
	if expires_at and expires_at > time.monotonic():
		return True

	try:
		member = await bot.get_chat_member(SUBSCRIPTION_CHAT_ID, user_id)
	except TelegramError:
		LOGGER.exception(
			"Cannot check subscription for user %s in %s; letting the user through",
			user_id,
			SUBSCRIPTION_CHAT_ID,
		)
		return True

	is_member = is_member_status(member)
	remember_membership(user_id, is_member)
	return is_member
