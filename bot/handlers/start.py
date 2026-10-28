"""Команды /start и /menu — точка входа и возврат к выбору языка."""

from __future__ import annotations

from telegram import Message, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import SUPPORTED_LANGUAGES
from bot.content.texts import START_TEXTS
from bot.database import register_user
from bot.keyboards import language_selection_keyboard

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


def greeting_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
	"""Язык приветствия: выбранный пользователем раньше, иначе язык его Telegram."""
	language = context.user_data.get("language")
	if language in SUPPORTED_LANGUAGES:
		return language
	telegram_language = (update.effective_user.language_code or "") if update.effective_user else ""
	return "uz" if telegram_language.startswith("uz") else "ru"


def _reset_transient_state(context: ContextTypes.DEFAULT_TYPE) -> None:
	for key in TRANSIENT_KEYS:
		context.user_data.pop(key, None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Регистрирует пользователя, приветствует его и показывает выбор языка."""
	if update.callback_query:
		await update.callback_query.answer()

	message = _reply_target(update)
	if not message:
		return ConversationHandler.END

	user = update.effective_user
	if user:
		register_user(user.id, user.username, user.first_name, user.last_name)
	_reset_transient_state(context)
	await message.reply_text(
		START_TEXTS[greeting_language(update, context)],
		reply_markup=language_selection_keyboard(),
	)
	return ConversationHandler.END


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Команда /menu: сбрасывает выбранную колонию и возвращает к выбору языка.

	Телефон и язык остаются: они сохранены в базе и повторно не запрашиваются.
	"""
	for key in ("colony", "colony_name", "menu_section"):
		context.user_data.pop(key, None)
	return await start(update, context)
