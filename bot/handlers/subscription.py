"""Проверка подписки пользователя на группу перед обработкой личных сообщений."""

from __future__ import annotations

from telegram import (
	ChatMemberRestricted,
	InlineKeyboardButton,
	InlineKeyboardMarkup,
	Update,
)
from telegram.ext import ApplicationHandlerStop, ContextTypes

from bot.config import SUBSCRIPTION_CHAT_ID, SUBSCRIPTION_GROUP_URL
from bot.content.texts import (
	COLONY_PROMPTS,
	LANGUAGE_BUTTONS,
	PHONE_PROMPTS,
	SUBSCRIPTION_BUTTONS,
	SUBSCRIPTION_PROMPTS,
	SUBSCRIPTION_WELCOME_TEXTS,
)
from bot.database import get_user_language, get_user_phone_number
from bot.handlers.start import start
from bot.keyboards import colony_group_keyboard, contact_request_keyboard


def is_language_selection_update(update: Update) -> bool:
	"""Проверяет, что пользователь запускает бота или выбирает язык."""
	message = update.message
	if not message or not message.text:
		return False

	text = message.text.strip()
	if text.split(maxsplit=1)[0].split("@", 1)[0] == "/start":
		return True

	language_labels = {label for label, _ in LANGUAGE_BUTTONS}
	language_labels.update(("O'zbekcha", "Русский", "Узбекча"))
	return text in language_labels


def subscription_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Показывает одну кнопку-ссылку для вступления в группу."""
	buttons = SUBSCRIPTION_BUTTONS.get(language, SUBSCRIPTION_BUTTONS["ru"])
	return InlineKeyboardMarkup(
		[[InlineKeyboardButton(buttons[0], url=SUBSCRIPTION_GROUP_URL)]]
	)


def _is_member_status(member: object) -> bool:
	return getattr(member, "status", None) in {"creator", "administrator", "member"} or (
		isinstance(member, ChatMemberRestricted) and member.is_member
	)


def _is_subscription_chat(chat: object) -> bool:
	configured_chat = str(SUBSCRIPTION_CHAT_ID)
	if configured_chat.startswith("@"):
		return getattr(chat, "username", None) == configured_chat[1:]
	try:
		return getattr(chat, "id", None) == int(configured_chat)
	except ValueError:
		return False


async def is_group_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
	"""Проверяет актуальное членство пользователя в обязательной группе."""
	user = update.effective_user
	if not user:
		return False

	member = await context.bot.get_chat_member(SUBSCRIPTION_CHAT_ID, user.id)
	return _is_member_status(member)


async def _welcome_new_member(
	user_id: int,
	context: ContextTypes.DEFAULT_TYPE,
	user_data: dict | None = None,
) -> None:
	user_data = user_data if user_data is not None else {}
	language = user_data.get("language") or get_user_language(user_id) or "ru"
	user_data["language"] = language
	user_data["subscription_welcomed"] = True

	await context.bot.send_message(
		chat_id=user_id,
		text=SUBSCRIPTION_WELCOME_TEXTS.get(
			language,
			SUBSCRIPTION_WELCOME_TEXTS["ru"],
		),
	)

	phone_number = get_user_phone_number(user_id)
	if phone_number:
		user_data["phone_number"] = phone_number
		await context.bot.send_message(
			chat_id=user_id,
			text=COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
			reply_markup=colony_group_keyboard(language),
		)
		return

	phone_prompt = PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])
	await context.bot.send_message(
		chat_id=user_id,
		text=phone_prompt["prompt"],
		reply_markup=contact_request_keyboard(language),
	)


async def handle_subscription_member(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Приветствует пользователя при вступлении и продолжает его онбординг."""
	change = update.chat_member
	if not change or not _is_subscription_chat(change.chat):
		return

	user = change.new_chat_member.user
	if user.is_bot:
		return

	actor = update.effective_user
	user_data = (
		context.user_data
		if actor and actor.id == user.id
		else {}
	)
	was_member = _is_member_status(change.old_chat_member)
	is_member = _is_member_status(change.new_chat_member)
	if is_member and not was_member and not user_data.get("subscription_welcomed"):
		await _welcome_new_member(user.id, context)
	elif not is_member:
		user_data.pop("subscription_welcomed", None)


async def prompt_group_subscription(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Предлагает вступить в группу на выбранном пользователем языке."""
	message = update.effective_message
	if not message:
		return

	language = context.user_data.get("language", "ru")
	prompt = SUBSCRIPTION_PROMPTS.get(language, SUBSCRIPTION_PROMPTS["ru"])
	await message.reply_text(
		prompt,
		reply_markup=subscription_keyboard(language),
	)


async def require_group_subscription(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Останавливает обработку личных обновлений, пока пользователь не состоит в группе."""
	user = update.effective_user
	chat = update.effective_chat
	if not user or user.is_bot or not chat or chat.type != "private":
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
	"""Обрабатывает старую кнопку проверки без повторного показа выбора языка."""
	query = update.callback_query
	user = update.effective_user
	if not query or query.data != "subscription:check" or not user:
		return

	await query.answer()
	user_data = context.user_data
	if not user_data.get("subscription_welcomed") and await is_group_member(update, context):
		await _welcome_new_member(user.id, context, user_data)
