"""Промежуточные обработчики личных сообщений: контекст пользователя и обязательная подписка."""

from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import Forbidden, TelegramError
from telegram.ext import ApplicationHandlerStop, ContextTypes

from bot.config import SUBSCRIPTION_GROUP_URL
from bot.content.texts import (
	COLONY_PROMPTS,
	PHONE_PROMPTS,
	SUBSCRIPTION_BUTTONS,
	SUBSCRIPTION_PROMPTS,
	SUBSCRIPTION_WELCOME_TEXTS,
)
from bot.database import get_user_language, get_user_phone_number
from bot.handlers.common import HTML, escape, step_header, user_language
from bot.handlers.patterns import LANGUAGE_LABELS
from bot.handlers.start import start
from bot.keyboards import colony_group_keyboard, contact_request_keyboard
from bot.services.subscription import (
	check_membership,
	is_member_status,
	is_subscription_chat,
	remember_membership,
)

LOGGER = logging.getLogger(__name__)


def _is_private_user_update(update: Update) -> bool:
	user = update.effective_user
	chat = update.effective_chat
	return bool(user and not user.is_bot and chat and chat.type == "private")


async def load_user_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Подтягивает язык и телефон пользователя из базы, если их нет в памяти бота."""
	if not _is_private_user_update(update):
		return

	user_data = context.user_data
	user_id = update.effective_user.id
	if "language" not in user_data:
		language = get_user_language(user_id)
		if language:
			user_data["language"] = language
	if "phone_number" not in user_data:
		phone_number = get_user_phone_number(user_id)
		if phone_number:
			user_data["phone_number"] = phone_number


def is_language_selection_update(update: Update) -> bool:
	"""Пользователь запускает бота или выбирает язык — это разрешено без подписки."""
	message = update.message
	if not message or not message.text:
		return False

	text = message.text.strip()
	command = text.split(maxsplit=1)[0].split("@", 1)[0]
	return command in ("/start", "/menu", "/help") or text in LANGUAGE_LABELS


def subscription_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Кнопка-ссылка для вступления в группу и кнопка повторной проверки."""
	join_text, check_text = SUBSCRIPTION_BUTTONS.get(language, SUBSCRIPTION_BUTTONS["ru"])
	return InlineKeyboardMarkup(
		[
			[InlineKeyboardButton(join_text, url=SUBSCRIPTION_GROUP_URL)],
			[InlineKeyboardButton(check_text, callback_data="subscription:check")],
		]
	)


async def is_group_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
	"""Проверяет членство текущего пользователя в обязательной группе."""
	user = update.effective_user
	if not user:
		return False
	return await check_membership(context.bot, user.id)


async def prompt_group_subscription(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Предлагает вступить в группу на языке пользователя."""
	message = update.effective_message
	if not message:
		return

	language = user_language(context)
	join_text, check_text = SUBSCRIPTION_BUTTONS.get(language, SUBSCRIPTION_BUTTONS["ru"])
	prompt = SUBSCRIPTION_PROMPTS.get(language, SUBSCRIPTION_PROMPTS["ru"]).format(
		join=escape(join_text),
		check=escape(check_text),
	)
	await message.reply_text(prompt, parse_mode=HTML, reply_markup=subscription_keyboard(language))


async def _welcome_new_member(
	user_id: int,
	context: ContextTypes.DEFAULT_TYPE,
	user_data: dict,
) -> None:
	"""Приветствует вступившего и продолжает онбординг: телефон или выбор колонии."""
	language = user_data.get("language") or get_user_language(user_id) or "ru"
	user_data["language"] = language
	user_data["subscription_welcomed"] = True

	welcome = SUBSCRIPTION_WELCOME_TEXTS.get(language, SUBSCRIPTION_WELCOME_TEXTS["ru"])
	phone_number = user_data.get("phone_number") or get_user_phone_number(user_id)
	if phone_number:
		user_data["phone_number"] = phone_number
		await context.bot.send_message(chat_id=user_id, text=welcome)
		await context.bot.send_message(
			chat_id=user_id,
			text=COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
			reply_markup=colony_group_keyboard(language),
		)
		return

	phone_prompt = escape(PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])["prompt"])
	await context.bot.send_message(
		chat_id=user_id,
		text=f"{escape(welcome)}\n\n{step_header(language, 2)}\n{phone_prompt}",
		parse_mode=HTML,
		reply_markup=contact_request_keyboard(language),
	)


async def handle_subscription_member(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Реагирует на вступление в группу и выход из неё."""
	change = update.chat_member
	if not change or not is_subscription_chat(change.chat):
		return

	user = change.new_chat_member.user
	if user.is_bot:
		return

	was_member = is_member_status(change.old_chat_member)
	is_member = is_member_status(change.new_chat_member)
	remember_membership(user.id, is_member)

	# user_data привязан к пользователю, совершившему действие; если его добавил
	# кто-то другой, берём данные самого вступившего из общего хранилища.
	actor = update.effective_user
	user_data = (
		context.user_data
		if actor and actor.id == user.id
		else context.application.user_data.get(user.id, {})
	)
	if not is_member:
		user_data.pop("subscription_welcomed", None)
		return
	if was_member or user_data.get("subscription_welcomed"):
		return
	# Пишем только тем, кто уже запускал бота: остальным Telegram не даст отправить сообщение.
	if get_user_language(user.id) is None:
		return

	try:
		await _welcome_new_member(user.id, context, user_data)
	except Forbidden:
		LOGGER.info("User %s joined the group but has blocked the bot", user.id)
	except TelegramError:
		LOGGER.exception("Failed to welcome new group member %s", user.id)


async def require_group_subscription(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Останавливает обработку личных обновлений, пока пользователь не вступил в группу."""
	if not _is_private_user_update(update) or update.chat_member:
		return

	if is_language_selection_update(update):
		return

	if not context.user_data.get("language"):
		await start(update, context)
		raise ApplicationHandlerStop

	if await is_group_member(update, context):
		return

	if update.callback_query:
		await update.callback_query.answer()
	await prompt_group_subscription(update, context)
	raise ApplicationHandlerStop


async def handle_subscription_check(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Кнопка «Я вступил»: до неё доходят только подтверждённые участники группы."""
	query = update.callback_query
	user = update.effective_user
	if not query or not user:
		return

	await query.answer()
	if query.message:
		try:
			await query.edit_message_reply_markup(reply_markup=None)
		except TelegramError:
			pass
	await _welcome_new_member(user.id, context, context.user_data)
