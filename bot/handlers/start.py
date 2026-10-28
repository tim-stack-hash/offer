"""Команды /start и /menu — точка входа и возврат к выбору языка."""

from __future__ import annotations

from telegram import Message, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.database import register_user
from bot.keyboards import language_selection_keyboard

LANGUAGE_PROMPT = "🌐 Выберите язык / Tilni tanlang:"

# Временные состояния сценариев, которые сбрасываются при перезапуске меню.
TRANSIENT_KEYS = (
	"changing_language",
	"feedback_category",
	"pending_lawyer_review",
	"lawyer_region",
	"lawyer_id",
	"clothing_region",
)


def _reply_target(update: Update) -> Message | None:
	if update.message:
		return update.message
	query = update.callback_query
	if query and isinstance(query.message, Message):
		return query.message
	return None


def _reset_transient_state(context: ContextTypes.DEFAULT_TYPE) -> None:
	for key in TRANSIENT_KEYS:
		context.user_data.pop(key, None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Регистрирует пользователя и показывает выбор языка."""
	if update.callback_query:
		await update.callback_query.answer()

	message = _reply_target(update)
	if not message:
		return ConversationHandler.END

	user = update.effective_user
	if user:
		register_user(user.id, user.username, user.first_name, user.last_name)
	_reset_transient_state(context)
	await message.reply_text(LANGUAGE_PROMPT, reply_markup=language_selection_keyboard())
	return ConversationHandler.END


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Команда /menu: сбрасывает выбранную колонию и возвращает к выбору языка.

	Телефон и язык остаются: они сохранены в базе и повторно не запрашиваются.
	"""
	for key in ("colony", "colony_name", "menu_section"):
		context.user_data.pop(key, None)
	return await start(update, context)
